"""Hardware-independent state machine binding historical decisions to vision.

No serial, camera or hardware imports: may be exercised using simulated packets.
"""
from dataclasses import dataclass
from .decision import Controller
from .protocol import SensorPacket
from .vision import VisionWorker


@dataclass(frozen=True)
class CycleResult:
    result: int
    people: int
    detection_started: bool
    vision_pending: bool
    vision_failed: bool
    reason: str


class Coordinator:
    def __init__(self, controller: Controller, vision: VisionWorker,
                 detect_always: bool = False, stop_while_inflight: bool = True):
        self.controller = controller
        self.vision = vision
        self.detect_always = detect_always
        self.stop_while_inflight = stop_while_inflight

    def process(self, packet: SensorPacket, now: float) -> CycleResult:
        if packet.button and not self.controller.button_was_pressed:
            self.vision.invalidate()  # discard pre-restart detections
        self.vision.poll()
        started = False
        # If the button has been pressed or the ignore period is active,
        # skip new camera calculations and preserve permission=1.
        if self.controller.should_detect(packet, now, self.detect_always):
            started = self.vision.request(now)
        self.vision.poll()  # also accepts immediately-completed synthetic tasks
        people = self.vision.last_people if self.vision.valid else 0
        result = self.controller.update(packet, people, now)
        ignoring = packet.button or now < self.controller.ignore_until
        pending = self.vision.future is not None
        reason = 'historical decision'
        if not ignoring and self.vision.failed:
            result = 0
            self.controller.previous_result = 0
            reason = 'vision error -> STOP'
        elif not ignoring and pending and self.stop_while_inflight:
            # Prevent entering a monitored area while a fresh frame is being analyzed.
            result = 0
            self.controller.previous_result = 0
            reason = 'vision pending -> STOP'
        elif ignoring:
            reason = 'restart/ignore override'
        return CycleResult(result, people, started, pending, self.vision.failed, reason)

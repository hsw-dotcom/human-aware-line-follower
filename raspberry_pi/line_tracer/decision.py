"""Recorded final decision rule and restart-ignore behavior (reconstructed)."""
from dataclasses import dataclass
from .protocol import SensorPacket


def decide_result(packet: SensorPacket, people_num: int, previous_result: int) -> int:
    """The final rule described in the user's historical notes.

    1. Button pressed -> 1
    2. Red color rule OR any person -> 0
    3. Otherwise retain previous result.
    """
    if previous_result not in (0, 1):
        raise ValueError('previous_result must be 0 or 1')
    if people_num < 0:
        raise ValueError('people_num must be non-negative')
    if packet.button == 1:
        return 1
    if packet.color_condition or people_num != 0:
        return 0
    return previous_result


@dataclass
class Controller:
    """Reference integration of 'button -> restart, ignore stop for 1~3s'."""
    restart_ignore_seconds: float = 2.0
    previous_result: int = 1
    ignore_until: float = 0.0
    button_was_pressed: bool = False

    def update(self, packet: SensorPacket, people_num: int, now: float) -> int:
        if packet.button:
            if not self.button_was_pressed:
                self.ignore_until = now + self.restart_ignore_seconds
            self.button_was_pressed = True
            self.previous_result = 1
            return 1
        self.button_was_pressed = False
        if now < self.ignore_until:
            self.previous_result = 1
            return 1
        self.previous_result = decide_result(packet, people_num, self.previous_result)
        return self.previous_result

    def should_detect(self, packet: SensorPacket, now: float, detect_always: bool = False) -> bool:
        if packet.button or now < self.ignore_until:
            return False
        # The specific colored floor zone starts camera analysis.
        # Optionally detect outside the zone as a reconstructed extension.
        return detect_always or packet.color_condition or self.previous_result == 0

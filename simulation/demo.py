"""No-hardware simulation of the reconstructed rules.

From project root: python3 simulation/demo.py
"""
from pathlib import Path
import sys
from concurrent.futures import Future

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from line_tracer.coordinator import Coordinator
from line_tracer.decision import Controller
from line_tracer.protocol import parse_packet
from line_tracer.vision import VisionWorker


class ImmediateExecutor:
    def submit(self, fn):
        future = Future()
        try:
            future.set_result(fn())
        except Exception as error:
            future.set_exception(error)
        return future


frame_counts = iter([1, 0, 0])
vision = VisionWorker(lambda: next(frame_counts), executor=ImmediateExecutor(), interval_seconds=0.0)
control = Coordinator(Controller(restart_ignore_seconds=2.0), vision)
scenarios = [
    (0.0, '2:3:3:0', 'no trigger / line follow'),
    (1.0, '5:1:1:0', 'marker detection / stop'),
    (1.5, '5:1:1:1', 'restart button'),
    (2.0, '5:1:1:0', 'ignore window'),
    (3.2, '2:3:3:0', 'ignore expires, previous state remains 1'),
    (4.0, '5:1:1:0', 'next marker / stop'),
]
for now, raw, note in scenarios:
    state = control.process(parse_packet(raw), now)
    print(f't={now:>4.1f}s rx={raw:>8s} people={state.people} result={state.result} ({note})')

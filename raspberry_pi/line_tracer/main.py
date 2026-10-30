"""2023 line-tracer serial/camera reconstruction; NOT historical source.

Camera capture/detection runs in one worker thread so serial replies are not
held up by inference. This is a safety/reliability enhancement over a likely
synchronous original; the control predicates remain recorded historical rules.
"""
import argparse
import configparser
import logging
import time
from pathlib import Path

from .camera import SnapshotCamera
from .coordinator import Coordinator
from .count_objects import detect
from .decision import Controller
from .detector_adapter import people_count
from .protocol import encode_result, parse_packet
from .vision import VisionWorker

LOG = logging.getLogger('line_tracer')


def run(config_path: Path):
    import serial
    settings = configparser.ConfigParser()
    if not settings.read(config_path, encoding='utf-8'):
        raise FileNotFoundError(config_path)
    port = settings.get('serial', 'port')
    baud = settings.getint('serial', 'baudrate', fallback=9600)
    read_timeout = settings.getfloat('serial', 'timeout_seconds', fallback=0.2)
    width = settings.getint('camera', 'width', fallback=640)
    height = settings.getint('camera', 'height', fallback=480)
    path = Path(settings.get('camera', 'snapshot_path', fallback='runtime/before.jpg'))
    ignore = settings.getfloat('control', 'restart_ignore_seconds', fallback=2.0)
    always = settings.getboolean('control', 'detect_always', fallback=False)
    interval = settings.getfloat('control', 'minimum_capture_interval_seconds', fallback=0.5)
    stop_pending = settings.getboolean('control', 'stop_while_inflight', fallback=True)
    if not 1.0 <= ignore <= 3.0:
        raise ValueError('historically tested restart_ignore_seconds range is 1~3')

    with serial.Serial(port=port, baudrate=baud, timeout=read_timeout,
                       write_timeout=0.5) as com:
        time.sleep(2.0)  # USB serial may reset Arduino; duration is assumed
        # Discard boot messages / partial requests on startup.
        com.reset_input_buffer()
        with SnapshotCamera(width, height) as camera:
            def sample():
                # Historical order: before.jpg -> count_objects.detect().
                camera.snapshot(path)
                return people_count(detect(path))

            with VisionWorker(sample, interval_seconds=interval) as vision:
                logic = Controller(restart_ignore_seconds=ignore)
                coordinator = Coordinator(logic, vision, always, stop_pending)
                LOG.info('Connected on %s @%s, image=%s', port, baud, path)
                while True:
                    line = com.readline()
                    if not line:
                        # Arduino independently stops on reply timeout.
                        continue
                    try:
                        packet = parse_packet(line)
                    except ValueError as error:
                        LOG.warning('Malformed Arduino packet %r: %s', line[:80], error)
                        # Complete invalid requests get a fail-safe reply to avoid
                        # unnecessary timeout. For unknown extra lines, do not
                        # assume a valid command.
                        com.write(encode_result(0))
                        continue
                    reason = 'failsafe'
                    try:
                        state = coordinator.process(packet, time.monotonic())
                        reply = state.result
                        reason = state.reason
                    except Exception:
                        LOG.exception('Control failure; STOP')
                        logic.previous_result = 0
                        reply = 0
                    com.write(encode_result(reply))
                    LOG.info('rx=%s:%s:%s:%s people=%d pending=%s tx=%d %s',
                             packet.r, packet.g, packet.b, packet.button,
                             vision.last_people if vision.valid else 0,
                             vision.future is not None, reply,
                             reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('config.ini'))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    try:
        run(args.config)
    except KeyboardInterrupt:
        LOG.info('stopped')


if __name__ == '__main__':
    main()

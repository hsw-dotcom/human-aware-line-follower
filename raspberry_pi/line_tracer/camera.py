"""Reference Picamera2 adapter. Pi-specific dependency imported only at runtime."""
from pathlib import Path


class SnapshotCamera:
    def __init__(self, width=640, height=480):
        from picamera2 import Picamera2
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(
            main={'size': (width, height), 'format': 'RGB888'}))

    def __enter__(self):
        self.camera.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.camera.stop()
        self.camera.close()

    def snapshot(self, target: str | Path) -> Path:
        import cv2
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        rgb = self.camera.capture_array()
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        if not cv2.imwrite(str(target), bgr):
            raise OSError(f'failed to write snapshot: {target}')
        return target

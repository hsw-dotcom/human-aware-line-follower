"""Asynchronous vision for prompt serial responses (modern reconstruction).

The real 2023 code may have performed capture/detection synchronously. This
worker is an explicit enhancement to avoid an Arduino timeout during inference.
Only one camera/detector task can run at a time.
"""
from concurrent.futures import Executor, Future, ThreadPoolExecutor
from typing import Callable, Optional


class VisionWorker:
    def __init__(self, sample: Callable[[], int], executor: Optional[Executor] = None,
                 interval_seconds: float = 0.5):
        if interval_seconds < 0:
            raise ValueError('interval_seconds must be non-negative')
        self.sample = sample
        self._executor = executor or ThreadPoolExecutor(max_workers=1, thread_name_prefix='vision')
        self._owns_executor = executor is None
        self.interval_seconds = interval_seconds
        self.future: Optional[Future] = None
        self.future_epoch = 0
        self.epoch = 0
        self.last_started_at: Optional[float] = None
        self.last_people = 0
        self.valid = False
        self.failed = False
        self.last_error = ''

    def poll(self) -> None:
        if self.future is None or not self.future.done():
            return
        f = self.future
        epoch = self.future_epoch
        self.future = None
        try:
            count = f.result()
            if type(count) is not int or count < 0:
                raise ValueError('sample() must return a non-negative int')
        except Exception as error:
            if epoch == self.epoch:
                self.failed = True
                self.valid = False
                self.last_error = f'{type(error).__name__}: {error}'
            return
        if epoch == self.epoch:
            self.last_people = count
            self.valid = True
            self.failed = False
            self.last_error = ''

    def request(self, now: float) -> bool:
        self.poll()
        if self.future is not None:
            return False
        if self.last_started_at is not None and now - self.last_started_at < self.interval_seconds:
            return False
        self.last_started_at = now
        self.future_epoch = self.epoch
        self.future = self._executor.submit(self.sample)
        return True

    def invalidate(self) -> None:
        """Discard results recorded before restart; a running task may finish."""
        self.epoch += 1
        self.valid = False
        self.failed = False
        self.last_people = 0
        self.last_error = ''
        self.last_started_at = None

    def close(self) -> None:
        if self._owns_executor:
            self._executor.shutdown(wait=True)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()

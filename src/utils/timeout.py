import os
import signal
import threading
import _thread

class Timeout:
    """Real-time limit that also funciona no Windows."""

    def __init__(self, seconds: int) -> None:
        self.seconds = seconds
        self._timer: threading.Timer | None = None

    def __enter__(self):
        if os.name == "posix":
            signal.signal(signal.SIGALRM, self._raise_timeout)
            signal.alarm(self.seconds)
        else:
            self._timer = threading.Timer(self.seconds, _thread.interrupt_main)
            self._timer.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        if os.name == "posix":
            signal.alarm(0)
        elif self._timer:
            self._timer.cancel()
        return False

    @staticmethod
    def _raise_timeout(signum, frame):
        raise TimeoutError

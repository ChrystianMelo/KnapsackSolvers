import os
import signal

class Timeout:
    """Context‑manager enforcing a real‑time limit via ``signal.alarm`` (POSIX)."""

    def __init__(self, seconds: int) -> None:
        self.seconds = seconds

    def __enter__(self):
        if os.name == "posix":
            signal.signal(signal.SIGALRM, self._raise_timeout)
            signal.alarm(self.seconds)
        return self

    def __exit__(self, exc_type, exc, tb):
        if os.name == "posix":
            signal.alarm(0)  # cancel
        return False  # propagate any exception

    @staticmethod
    def _raise_timeout(signum, frame):  # noqa: D401,N802 – signal handler sig
        raise TimeoutError
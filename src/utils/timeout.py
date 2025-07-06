import os
import signal
import threading
import _thread


class Timeout:
    '''Context manager que aborta o bloco se exceder o tempo limite.'''

    def __init__(self, seconds: int) -> None:
        '''Armazena o limite em segundos e prepara o timer adequado.'''
        self.seconds = seconds
        self._timer: threading.Timer | None = None

    def __enter__(self):
        '''Inicia sinal/timer que lançará TimeoutError ao expirar.'''
        if os.name == "posix":
            signal.signal(signal.SIGALRM, self._raise_timeout)
            signal.alarm(self.seconds)
        else:
            self._timer = threading.Timer(self.seconds, _thread.interrupt_main)
            self._timer.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        '''Cancela o alarme/timer ao sair do contexto.'''
        if os.name == "posix":
            signal.alarm(0)
        elif self._timer:
            self._timer.cancel()
        return False

    @staticmethod
    def _raise_timeout(signum, frame):
        '''Cancela o alarme/timer ao sair do contexto.'''
        raise TimeoutError

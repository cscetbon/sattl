import signal
import time
import sys


class TimeoutException(Exception):
    pass


class Timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, *_):
        raise TimeoutException(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, *_):
        signal.alarm(0)


class RetryWithTimeout:
    def __init__(self, func, seconds):
        try:
            with Timeout(seconds=seconds):
                while True:
                    try:
                        func()
                        break
                    except:
                        self.last_exception = sys.exc_info()[1]
                        time.sleep(5)
        except TimeoutException:
            raise TimeoutException(self.last_exception)

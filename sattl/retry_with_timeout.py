import signal
import time
import sys
from sattl.logger import logger


class TimeoutException(Exception):
    pass


def _handle_timeout(*_):
    raise TimeoutException("Timeout")


class Timeout:
    def __init__(self, timeout=1):
        self.seconds = timeout


    def __enter__(self):
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, *_):
        signal.alarm(0)


class RetryWithTimeout:
    def __init__(self, func, timeout, retry_delay=5):
        self.last_exception = ""
        try:
            with Timeout(timeout):
                while True:
                    try:
                        func()
                        break
                    except TimeoutException:
                        raise
                    except:
                        logger.info(f"Operation failed, retrying in {retry_delay} seconds")
                        self.last_exception = sys.exc_info()[1]
                        time.sleep(retry_delay)
        except TimeoutException:
            raise TimeoutException(self.last_exception)

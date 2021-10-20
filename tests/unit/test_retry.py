from sattl.retry_with_timeout import TimeoutException, RetryWithTimeout
import time

import pytest
from mock import Mock


def test_retry_exceeds_timeout():
    with pytest.raises(TimeoutException):
        RetryWithTimeout(lambda: time.sleep(10), timeout=1)


def test_retry_fails():
    with pytest.raises(TimeoutException):
        RetryWithTimeout(Mock(side_effect=Exception), timeout=1)


def test_retry_succeeds():
    RetryWithTimeout(lambda: time.sleep(1), timeout=2)


def test_retry_succeeds_after_2_tries():
    RetryWithTimeout(Mock(side_effect=[Exception, Exception, 2]), timeout=1, retry_delay=0)

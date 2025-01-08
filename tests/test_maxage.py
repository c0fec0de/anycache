"""Age Testing."""

import datetime
import time

import pytest

from anycache import AnyCache


def test_maxage_none():
    """Disable maximum age check."""
    ac = AnyCache(maxage=None)

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    time.sleep(5)
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1


@pytest.mark.parametrize(
    argnames=("maxage_seconds", "wait_seconds"),
    argvalues=[
        (1, 5),
        (2, 5),
        (3, 5),
    ],
)
def test_maxage_expired_cache(
    maxage_seconds: int,
    wait_seconds: int,
    threshold_seconds: int = 1,
):
    """Small, basic maximum age check."""
    ac = AnyCache(maxage=datetime.timedelta(seconds=maxage_seconds))

    @ac.anycache()
    def myfunc():
        # count the number of calls
        myfunc.callcount += 1
        return datetime.datetime.now(tz=datetime.timezone.utc)

    myfunc.callcount = 0

    # Ensure that the returned datetime value is within the acceptable threshold from
    # when the function was invoked and that the function was invoked once.
    difference = datetime.datetime.now(tz=datetime.timezone.utc) - myfunc()
    assert difference <= datetime.timedelta(seconds=threshold_seconds)
    assert myfunc.callcount == 1

    # Wait the given amount of time.
    time.sleep(wait_seconds)

    # Ensure that the returned datetime value is within the acceptable threshold from
    # when the function was invoked and that the function was invoked a second time.
    difference = datetime.datetime.now(tz=datetime.timezone.utc) - myfunc()
    assert difference <= datetime.timedelta(seconds=threshold_seconds)
    assert myfunc.callcount == 2


@pytest.mark.parametrize(
    argnames=("maxage_seconds", "wait_seconds"),
    argvalues=[
        (60, 1),
        (60, 2),
        (60, 3),
    ],
)
def test_maxage_nonexpired_cache(
    maxage_seconds: int,
    wait_seconds: int,
    threshold_seconds: int = 1,
):
    """Small, basic maximum age check."""
    ac = AnyCache(maxage=datetime.timedelta(seconds=maxage_seconds))

    @ac.anycache()
    def myfunc():
        # count the number of calls
        myfunc.callcount += 1
        return datetime.datetime.now(tz=datetime.timezone.utc)

    myfunc.callcount = 0

    # Ensure that the returned datetime value is within the acceptable threshold from
    # when the function was invoked and that the function was invoked once.
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    difference = now - myfunc()
    assert difference <= datetime.timedelta(seconds=threshold_seconds)
    assert myfunc.callcount == 1

    # Wait the given amount of time.
    time.sleep(wait_seconds)

    # Ensure that the returned datetime value is within the acceptable threshold from
    # when the function was invoked and that the function was still only invoked once.
    difference = now - myfunc()
    assert difference <= datetime.timedelta(seconds=threshold_seconds)
    assert myfunc.callcount == 1

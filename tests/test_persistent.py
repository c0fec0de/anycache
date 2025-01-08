"""Persistency Testing."""

from pathlib import Path

from anycache import AnyCache


def test_persistent(tmp_path):
    """Persistent Cache over multiple instances."""
    cachedir = tmp_path
    ac = AnyCache(cachedir=cachedir)

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 2) == 6
    assert myfunc.callcount == 2

    del ac
    assert len(tuple(Path(cachedir).glob("*.cache"))) == 2

    ac = AnyCache(cachedir=cachedir)

    # pylint: disable=function-redefined
    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 0
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 0
    assert myfunc(4, 2) == 6
    assert myfunc.callcount == 0

    ac.clear()

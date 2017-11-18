from pathlib import Path
from tempfile import mkdtemp

from nose.tools import eq_

from anycache import AnyCache


def test_persistent():
    """Persistent Cache over multiple instances."""
    cachedir = Path(mkdtemp())
    ac = AnyCache(cachedir=cachedir)

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg
    myfunc.callcount = 0

    eq_(myfunc(4, 5), 9)
    eq_(myfunc.callcount, 1)
    eq_(myfunc(4, 5), 9)
    eq_(myfunc.callcount, 1)
    eq_(myfunc(4, 2), 6)
    eq_(myfunc.callcount, 2)

    del ac
    eq_(len(tuple(Path(cachedir).glob("*.cache"))), 2)

    ac = AnyCache(cachedir=cachedir)

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg
    myfunc.callcount = 0

    eq_(myfunc(4, 5), 9)
    eq_(myfunc.callcount, 0)
    eq_(myfunc(4, 5), 9)
    eq_(myfunc.callcount, 0)
    eq_(myfunc(4, 2), 6)
    eq_(myfunc.callcount, 0)

    ac.clear()

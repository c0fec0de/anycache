from pathlib import Path
from tempfile import mkdtemp

from nose.tools import eq_

from anycache import AnyCache


def test_is_outdated_and_remove():
    """is_outdated(), remove()."""

    ac = AnyCache()

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg
    myfunc.callcount = 0


    eq_(ac.is_outdated(myfunc, 3), True)
    eq_(ac.is_outdated(myfunc, 3), True)
    eq_(myfunc.callcount, 0)

    eq_(myfunc(3), 6)

    eq_(myfunc.callcount, 1)
    eq_(ac.is_outdated(myfunc, 3), False)
    eq_(ac.is_outdated(myfunc, 3), False)

    ac.remove(myfunc, 3)

    eq_(myfunc.callcount, 1)
    eq_(ac.is_outdated(myfunc, 3), True)

    eq_(myfunc(3), 6)

    eq_(myfunc.callcount, 2)
    eq_(ac.is_outdated(myfunc, 3), False)

    ac.remove(myfunc, 3)
    ac.remove(myfunc, 3)
    eq_(ac.is_outdated(myfunc, 3), True)


def test_ident():


    ac = AnyCache()

    @ac.anycache()
    def onefunc(posarg, kwarg=3):
        return posarg + kwarg

    @ac.anycache()
    def otherfunc(posarg, kwarg=3):
        return posarg + kwarg


    eq_(ac.get_ident(onefunc, 3), 'e41fb232f3d486a830bb807545ef52be582e907d505e7275a40d040b53bfe6a5')
    eq_(ac.get_ident(onefunc, 3, 3), '762c17e6404375af3a788bf29a0e92327c8d89383b1dacd1d6e80260b2d48500')
    eq_(ac.get_ident(onefunc, 4), 'e0e1f954b03011a72ce56802da766b3ab613b3f63b894bb43d353140bef0a5ea')
    eq_(ac.get_ident(otherfunc, 4), '731001353ec04a1d6247224866b20b274a77943a7bb6e57bfad5ceb86cc0eebe')

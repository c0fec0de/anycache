"""Advanced Test."""

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

    assert ac.is_outdated(myfunc, 3) is True
    assert ac.is_outdated(myfunc, 3) is True
    assert myfunc.callcount == 0

    assert myfunc(3) == 6

    assert myfunc.callcount == 1
    assert ac.is_outdated(myfunc, 3) is False
    assert ac.is_outdated(myfunc, 3) is False

    ac.remove(myfunc, 3)

    assert myfunc.callcount == 1
    assert ac.is_outdated(myfunc, 3) is True

    assert myfunc(3) == 6

    assert myfunc.callcount == 2
    assert ac.is_outdated(myfunc, 3) is False

    ac.remove(myfunc, 3)
    ac.remove(myfunc, 3)
    assert ac.is_outdated(myfunc, 3) is True


def test_ident():
    """Test Identifier."""
    ac = AnyCache()

    @ac.anycache()
    def onefunc(posarg, kwarg=3):
        return posarg + kwarg

    @ac.anycache()
    def otherfunc(posarg, kwarg=3):
        return posarg + kwarg

    assert ac.get_ident(onefunc, 3) == "ffc820e66d8ea34994ca144ba64eaf3ba7bcb206b23d8e2ed751f0cbe38aaa4a"
    assert ac.get_ident(onefunc, 3, 3) == "3598b087e7b7178b80adb148bff1719fb21259b2b2aa4cb89c524c8bafc54c22"
    assert ac.get_ident(onefunc, 4) == "6034f77e3dd288e56441542d920b08006d09bd1556f671f9441fd0cfb71191e6"
    assert ac.get_ident(otherfunc, 4) == "1ad95cc9af9d7ce53194fd534c9f480088d1a9faab5a5cd9fbdfb92163239f64"

# MIT License
#
# Copyright (c) 2017-2025 c0fec0de
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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

    assert ac.get_ident(onefunc, 3) == "2dc29acbe259ca42d88648c246c70c0fa9a328eb529a42804051d0aa592b8574"
    assert ac.get_ident(onefunc, 3, 3) == "b552415fb871ada190211077d70fb6b199eb57c6cbcc0ad2d78821d5b5c7ed6c"
    assert ac.get_ident(onefunc, 4) == "002326cb67f0edb72b0ec7c4d1ca20779dbd4423dc5ac3048f783184e95e4700"
    assert ac.get_ident(otherfunc, 4) == "60b29559de5889b6f378e25654bb90c6a9aaebeb63b52025b625e27e3e14b2c9"

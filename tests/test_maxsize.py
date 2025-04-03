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

"""Size Testing."""

from time import sleep

from anycache import AnyCache


def test_maxsize_0():
    """Disable Caching."""
    ac = AnyCache(maxsize=0)

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 2) == 6
    assert myfunc.callcount == 2
    assert myfunc(4, 2) == 6
    assert myfunc.callcount == 3
    assert ac.size == 0


def test_maxsize_none():
    """Unlimited Caching."""
    ac = AnyCache(maxsize=None)

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 2) == 6
    size1 = ac.size
    n = 5
    calls = n * n

    for posarg in range(n):
        for kwarg in range(n):
            assert myfunc(posarg, kwarg) == posarg + kwarg
    assert calls * size1 == ac.size
    assert myfunc.callcount == calls

    ac.clear()
    assert ac.size == 0


def test_maxsize_value():
    """Limited Caching."""
    ac = AnyCache(maxsize=None)

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        sleep(3)  # wait for slow windows file system
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 2) == 6
    size1 = ac.size
    n = 3
    calls = n * n

    for maxsize in (5 * size1, 8 * size1):
        ac.clear()
        myfunc.callcount = 0
        ac.maxsize = maxsize

        for posarg in range(n):
            for kwarg in range(n):
                assert myfunc(posarg, kwarg) == posarg + kwarg
        assert maxsize == ac.size
        assert myfunc.callcount == calls
        # last should be in cache
        assert myfunc(posarg, kwarg) == posarg + kwarg
        assert maxsize == ac.size
        assert myfunc.callcount == calls

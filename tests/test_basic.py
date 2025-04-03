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

"""Test Basic."""

from anycache import AnyCache, anycache, get_defaultcache


def test_basic():
    """Basic functionality."""

    @anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 2) == 6
    assert myfunc.callcount == 2
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 2

    assert get_defaultcache().size > 0


def test_del():
    """Test Delete."""
    ac = AnyCache()

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        return posarg + kwarg

    assert myfunc(4, 5) == 9
    assert ac.size > 0

    del ac
    # we are not able to check anything here :-(


def test_cleanup():
    """Cleanup."""
    ac = AnyCache()
    cachedir = ac.cachedir

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        # count the number of calls
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    # first use
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 2) == 6
    assert myfunc.callcount == 2
    assert myfunc(4, 2) == 6
    assert myfunc.callcount == 2
    assert ac.size > 0

    # clear
    ac.clear()
    assert ac.size == 0
    assert not tuple(cachedir.glob("*"))

    # second use
    assert myfunc(4, 4) == 8
    assert myfunc.callcount == 3
    assert ac.size > 0

    # clear twice
    ac.clear()
    assert ac.size == 0
    ac.clear()
    assert ac.size == 0


def test_size():
    """Size."""
    ac = AnyCache()

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        return posarg + kwarg

    assert ac.size == 0
    assert len(tuple(ac.cachedir.glob("*.cache"))) == 0
    assert myfunc(4, 5) == 9
    assert len(tuple(ac.cachedir.glob("*.cache"))) == 1
    size1 = ac.size
    assert myfunc(4, 2) == 6
    assert ac.size == 2 * size1
    assert len(tuple(ac.cachedir.glob("*.cache"))) == 2


def test_corrupt_cache(tmp_path):
    """Corrupted Cache."""
    cachedir = tmp_path
    ac = AnyCache(cachedir=cachedir)

    @ac.anycache()
    def myfunc(posarg, kwarg=3):
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1

    # corrupt cache
    cachefilepath = next(iter(cachedir.glob("*.cache")))
    with open(str(cachefilepath), "w", encoding="utf-8") as cachefile:  # noqa: PTH123
        cachefile.write("foo")

    # repair
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 2
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 2

    # corrupt dep
    depfilepath = next(iter(cachedir.glob("*.dep")))
    with open(str(depfilepath), "w", encoding="utf-8") as depfile:  # noqa: PTH123
        depfile.write("foo")

    # repair
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 3
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 3

    ac.clear()


def test_cachedir(tmp_path):
    """Corrupted Cache."""
    cachedir = tmp_path

    @anycache(cachedir=cachedir)
    def myfunc(posarg, kwarg=3):
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1
    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 1

    # pylint: disable=function-redefined
    @anycache(cachedir=cachedir)
    def myfunc(posarg, kwarg=3):
        """Cached Function."""
        myfunc.callcount += 1
        return posarg + kwarg

    myfunc.callcount = 0

    assert myfunc(4, 5) == 9
    assert myfunc.callcount == 0


def class_test():
    """Custom Class."""

    class MyClass:
        """Example Class."""

        # pylint: disable=too-few-public-methods

        def __init__(self, posarg, kwarg=3):
            self.posarg = posarg
            self.kwarg = kwarg

        @anycache()
        def func(self, arg):
            """Cached Function."""
            return self.posarg + self.kwarg + arg

    a = MyClass(2, 4)
    b = MyClass(1, 3)

    assert a.func(6) == 12
    assert a.func(6) == 12

    assert b.func(6) == 10
    assert b.func(6) == 10
    assert a.func(6) == 12

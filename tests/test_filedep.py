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

"""File Dependency Testing."""

from time import sleep

from anycache import anycache

TOUCHTIME = 2


def test_filedepfunc(tmp_path):
    """File dependencies."""
    depfilepath1 = tmp_path / "dep1"
    depfilepath2 = tmp_path / "dep2"

    with depfilepath1.open(mode="w") as depfile1:
        with depfilepath2.open(mode="w") as depfile2:
            depfile1.write("dep1")
            depfile2.write("dep2")

            def depfilefunc(result, posarg, kwarg=3):
                # pylint: disable=unused-argument
                deps = [depfilepath1]
                if posarg == 4:
                    deps.append(depfilepath2)
                return [d for d in deps if d.exists()]

            @anycache(depfilefunc=depfilefunc)
            def myfunc(posarg, kwarg=3):
                # count the number of calls
                myfunc.callcount += 1
                return posarg + kwarg

            myfunc.callcount = 0

            assert myfunc(4, 5) == 9
            assert myfunc.callcount == 1
            assert myfunc(1, 5) == 6
            assert myfunc.callcount == 2
            assert myfunc(4, 5) == 9
            assert myfunc.callcount == 2

            sleep(TOUCHTIME)
            depfilepath1.touch()
            sleep(TOUCHTIME)

            assert myfunc(4, 5) == 9
            assert myfunc.callcount == 3
            assert myfunc(1, 5) == 6
            assert myfunc.callcount == 4

            assert myfunc(4, 5) == 9
            assert myfunc.callcount == 4
            assert myfunc(1, 5) == 6
            assert myfunc.callcount == 4

            sleep(TOUCHTIME)
            depfilepath2.touch()
            sleep(TOUCHTIME)

            assert myfunc(4, 5) == 9
            assert myfunc.callcount == 5
            assert myfunc(1, 5) == 6
            assert myfunc.callcount == 5

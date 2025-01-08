"""File Dependency Testing."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from time import sleep

from anycache import anycache

TOUCHTIME = 2


def test_filedepfunc():
    """File dependencies."""
    with NamedTemporaryFile("w") as depfile1:
        with NamedTemporaryFile("w") as depfile2:
            depfile1.write("dep1")
            depfile2.write("dep2")
            depfilepath1 = Path(depfile1.name)
            depfilepath2 = Path(depfile2.name)

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

            depfile2.close()
            assert not depfilepath2.exists()

            assert myfunc(4, 5) == 9
            assert myfunc.callcount == 6
            assert myfunc(4, 5) == 9
            assert myfunc.callcount == 6

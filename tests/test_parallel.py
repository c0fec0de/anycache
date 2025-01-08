"""Persistency Testing."""

import random
import time
from concurrent.futures import ThreadPoolExecutor

from anycache import AnyCache


def test_parallel(tmp_path):
    """Parallel."""
    cachedir = tmp_path
    maxsize = 100
    ac = AnyCache(cachedir=cachedir, maxsize=maxsize)

    random.seed(5)

    @ac.anycache()
    def myfunc(arg):
        time.sleep(0.05 * random.randrange(10))
        return [arg] * 10

    with ThreadPoolExecutor(max_workers=20) as exe:
        jobs = [exe.submit(myfunc, random.randrange(10)) for _ in range(100)]
        for job in jobs:
            assert job.result()

    size = sum(file.stat().st_size for file in cachedir.glob("*"))
    assert size < maxsize

[![PyPI Version](https://badge.fury.io/py/anycache.svg)](https://badge.fury.io/py/anycache)
[![Python Build](https://github.com/c0fec0de/anycache/actions/workflows/main.yml/badge.svg)](https://github.com/c0fec0de/anycache/actions/workflows/main.yml)
[![Documentation](https://readthedocs.org/projects/anycache/badge/?version=stable)](https://anycache.readthedocs.io/en/stable/?badge=stable)
[![Coverage Status](https://coveralls.io/repos/github/c0fec0de/anycache/badge.svg?branch=main)](https://coveralls.io/github/c0fec0de/anycache?branch=main)
[![python-versions](https://img.shields.io/pypi/pyversions/anycache.svg)](https://pypi.python.org/pypi/anycache)

# Cache any python object to file using improved pickling

* [Documentation](https://anycache.readthedocs.io/en/stable/)
* [PyPI](https://pypi.org/project/anycache/)
* [Sources](https://github.com/c0fec0de/anycache)
* [Issues](https://github.com/c0fec0de/anycache/issues)

## Installation

Installing it is pretty easy:

```bash
pip install anycache
```

## Getting Started

```python
>>> from anycache import anycache
>>> @anycache()
... def myfunc(posarg, kwarg=3):
...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
...     return posarg + kwarg
>>> myfunc(8, 5)
  Calcing 8 + 5 = 13
13
>>> myfunc(8, 5)
13
```

`anycache` caches nearly any python object. Also `lambda` statements.
It uses [dill](https://pypi.python.org/pypi/dill) as backend. An improved version of pythons built-in `pickle`.

To preserve the result between multiple python runs, set a persistent cache
directory.

```python
>>> from anycache import anycache
>>> @anycache(cachedir='/tmp/anycache.my')
... def myfunc(posarg, kwarg=3):
...     return posarg + kwarg
```

The `AnyCache` object serves additional functions for cache clearing and
size handling.


.. image:: https://badge.fury.io/py/anycache.svg
    :target: https://badge.fury.io/py/anycache

.. image:: https://img.shields.io/pypi/dm/anycache.svg?label=pypi%20downloads
   :target: https://pypi.python.org/pypi/anycache

.. image:: https://readthedocs.org/projects/anycache/badge/?version=latest
    :target: https://anycache.readthedocs.io/en/latest/?badge=latest

.. image:: https://coveralls.io/repos/github/c0fec0de/anycache/badge.svg
    :target: https://coveralls.io/github/c0fec0de/anycache

.. image:: https://readthedocs.org/projects/anycache/badge/?version=2.1.0
    :target: https://anycache.readthedocs.io/en/2.1.0/?badge=2.1.0

.. image:: https://img.shields.io/pypi/pyversions/anycache.svg
   :target: https://pypi.python.org/pypi/anycache

.. image:: https://img.shields.io/badge/code%20style-pep8-brightgreen.svg
   :target: https://www.python.org/dev/peps/pep-0008/

.. image:: https://img.shields.io/badge/code%20style-pep257-brightgreen.svg
   :target: https://www.python.org/dev/peps/pep-0257/

.. image:: https://img.shields.io/badge/linter-pylint-%231674b1?style=flat
   :target: https://www.pylint.org/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/github/contributors/c0fec0de/anycache.svg
   :target: https://github.com/c0fec0de/anycache/graphs/contributors/

.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
   :target: http://makeapullrequest.com

.. image:: https://img.shields.io/github/issues-pr/c0fec0de/anycache.svg
   :target: https://github.com/c0fec0de/anycache/pulls

.. image:: https://img.shields.io/github/issues-pr-closed/c0fec0de/anycache.svg
   :target: https://github.com/c0fec0de/anycache/pulls?q=is%3Apr+is%3Aclosed

To cache the result of a function, use the global unlimited anycache:

* Documentation_
* PyPI_
* GitHub_
* Changelog_
* Issues_
* Contributors_

.. _anycache: https://anycache.readthedocs.io/en//
.. _Documentation: https://anycache.readthedocs.io/en//
.. _PyPI: https://pypi.org/project/anycache//
.. _GitHub: https://github.com/c0fec0de/anycache
.. _Changelog: https://github.com/c0fec0de/anycache/releases
.. _Issues: https://github.com/c0fec0de/anycache/issues
.. _Contributors: https://github.com/c0fec0de/anycache/graphs/contributors

.. _getting_started:

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

`anycache` caches nearly any python object. Also `lambda` statements.
It uses Dill_ as backend. An improved version of pythons build-in `pickle`.

To preserve the result between multiple python runs, a persistent cache
directory needs to be set.

>>> from anycache import anycache
>>> @anycache(cachedir='/tmp/anycache.my')
... def myfunc(posarg, kwarg=3):
...     return posarg + kwarg

The `AnyCache` object serves additional functions for cache clearing and
size handling.

.. _Dill: https://pypi.python.org/pypi/dill

Installation
============

To install the `anycache` module run::

    pip install anycache

If you do not have write-permissions to the python installation, try::

    pip install anycache --user

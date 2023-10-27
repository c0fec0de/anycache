***********************
Cache Any Python Object
***********************

.. image:: https://badge.fury.io/py/anycache.svg
    :target: https://badge.fury.io/py/anycache

.. image:: https://img.shields.io/pypi/dm/anycache.svg?label=pypi%20downloads
   :target: https://pypi.python.org/pypi/anycache

.. image:: https://readthedocs.org/projects/anycache/badge/?version=latest
    :target: https://anycache.readthedocs.io/en/latest/?badge=latest

.. image:: https://coveralls.io/repos/github/c0fec0de/anycache/badge.svg
    :target: https://coveralls.io/github/c0fec0de/anycache

.. image:: https://readthedocs.org/projects/anycache/badge/?version=
    :target: https://anycache.readthedocs.io/en//?badge=

.. image:: https://api.codeclimate.com/v1/badges/e6d325d6fd23a93aab20/maintainability
   :target: https://codeclimate.com/github/c0fec0de/anycache/maintainability
   :alt: Maintainability

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

Cache any python object to file using improved pickling

* Documentation_
* PyPI_
* GitHub_
* Changelog_
* Issues_
* Contributors_
.. toctree::
   :maxdepth: 2

   installation
   api

.. _anycache: https://anycache.readthedocs.io/en/2.1.0/
.. _Documentation: https://anycache.readthedocs.io/en/2.1.0/
.. _PyPI: https://pypi.org/project/anycache/2.1.0/
.. _GitHub: https://github.com/c0fec0de/anycache
.. _Changelog: https://github.com/c0fec0de/anycache/releases
.. _Issues: https://github.com/c0fec0de/anycache/issues
.. _Contributors: https://github.com/c0fec0de/anycache/graphs/contributors


Getting started
===============

.. _getting_started:

To cache the result of a function, use the global unlimited anycache:

>>> from anycache import anycache
>>> @anycache()
... def myfunc(posarg, kwarg=3):
...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
...     return posarg + kwarg
>>> myfunc(8, 10)
  Calcing 8 + 10 = 18
18
>>> myfunc(8, 10)
18

`anycache` caches nearly any python object. Also `lambda` statements.
It uses Dill_ as backend, an improved version of pythons build-in `pickle`.

Set a persistent cache directory to preserve the result between multiple python runs:

>>> from anycache import anycache
>>> @anycache(cachedir='/tmp/anycache.my')
... def myfunc(posarg, kwarg=3):
...     return posarg + kwarg

The :any:`AnyCache` object serves additional functions for cache clearing and
size handling.

.. _Dill: https://pypi.python.org/pypi/dill

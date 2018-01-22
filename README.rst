.. image:: https://badge.fury.io/py/anycache.svg
    :target: https://badge.fury.io/py/anycache

.. image:: https://travis-ci.org/c0fec0de/anycache.svg?branch=master
    :target: https://travis-ci.org/c0fec0de/anycache

.. image:: https://coveralls.io/repos/github/c0fec0de/anycache/badge.svg
    :target: https://coveralls.io/github/c0fec0de/anycache

.. image:: https://readthedocs.org/projects/anycache/badge/?version=2.0.4
    :target: http://anycache.readthedocs.io/en/2.0.4/?badge=2.0.4

.. image:: https://codeclimate.com/github/c0fec0de/anycache.png
    :target: https://codeclimate.com/github/c0fec0de/anycache

.. image:: https://img.shields.io/pypi/pyversions/anycache.svg
   :target: https://pypi.python.org/pypi/anycache

.. image:: https://landscape.io/github/c0fec0de/anycache/master/landscape.svg?style=flat
   :target: https://landscape.io/github/c0fec0de/anycache/master

.. image:: https://img.shields.io/badge/code%20style-pep8-brightgreen.svg
   :target: https://www.python.org/dev/peps/pep-0008/

.. image:: https://img.shields.io/badge/code%20style-pep257-brightgreen.svg
   :target: https://www.python.org/dev/peps/pep-0257/

Cache any python object to file using improved pickling

Documentation
=============

The Documentation_ is hosted on http://anycache.readthedocs.io/en/2.0.4/

.. _Documentation: http://anycache.readthedocs.io/en/2.0.4/

Getting started
===============

.. _getting_started:

To cache the result of a function, use the global unlimited anycache:

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

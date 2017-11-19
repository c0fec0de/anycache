***********************
Cache Any Python Object
***********************

.. image:: https://badge.fury.io/py/anycache.svg
    :target: https://badge.fury.io/py/anycache

.. image:: https://travis-ci.org/c0fec0de/anycache.svg?branch=master
    :target: https://travis-ci.org/c0fec0de/anycache

.. image:: https://coveralls.io/repos/github/c0fec0de/anycache/badge.svg
    :target: https://coveralls.io/github/c0fec0de/anycache

.. image:: https://readthedocs.org/projects/anycache/badge/?version=1.0.dev1
    :target: http://anycache.readthedocs.io/en/1.0.dev1/?badge=1.0.dev1

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

.. toctree::
   :maxdepth: 2

   installation
   api


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

To preserve the result between multiple python runs, a persistent cache
directory needs to be set at a central :any:`AnyCache` instance.

>>> from anycache import AnyCache
>>> ac = AnyCache(cachedir='/tmp/anycache.my')
>>> @ac.anycache()
... def myfunc(posarg, kwarg=3):
...     return posarg + kwarg

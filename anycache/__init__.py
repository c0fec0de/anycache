"""Cache any python object to file."""

import collections
import hashlib
import logging
import pathlib
import sys
import tempfile

import dill as pickle  # improved pickle

__version__ = "1.1.0"
__author__ = "c0fec0de"
__author_email__ = "c0fec0de@gmail.com"
__description__ = """Cache any python object to file using improved pickling ."""
__url__ = "https://github.com/c0fec0de/anycache"


_CacheEntry = collections.namedtuple("_CacheEntry", ("ident", "data", "dep"))
_CacheEntryInfo = collections.namedtuple("_CacheEntryInfo", ("ce", "mtime", "size"))
_FuncInfo = collections.namedtuple("FuncInfo", ("func", "args", "kwargs", "depfilefunc"))

if sys.version_info[0] < 3:  # pragma: no cover
    _bytes = bytes
else:
    def _bytes(name):
        return bytes(name, encoding='utf-8')

_CACHE_SUFFIX = ".cache"
_DEP_SUFFIX = ".dep"


class _CacheInfo(object):

    def __init__(self, cachedir):
        datafilepaths = cachedir.glob("*%s" % _CACHE_SUFFIX)
        self.cacheentries = [_CacheInfo.create_ce_from_datafilepath(d) for d in datafilepaths]
        self.cacheentryinfos = [_CacheInfo.create_cei(ce) for ce in self.cacheentries]
        self.totalsize = sum([cei.size for cei in self.cacheentryinfos])

    @staticmethod
    def create_ce_from_ident(cachedir, ident):
        data = cachedir / (ident + _CACHE_SUFFIX)
        dep = cachedir / (ident + _DEP_SUFFIX)
        return _CacheEntry(ident, data, dep)

    @staticmethod
    def create_ce_from_datafilepath(datafilepath):
        ident = datafilepath.name
        data = datafilepath
        dep = datafilepath.with_suffix(_DEP_SUFFIX)
        return _CacheEntry(ident, data, dep)

    @staticmethod
    def create_cei(ce):
        mtime = ce.data.stat().st_mtime
        size = ce.data.stat().st_size + ce.dep.stat().st_size
        return _CacheEntryInfo(ce, mtime, size)


class AnyCache(object):

    def __init__(self, cachedir=None, maxsize=None, debug=False):
        """
        Cache for python objects.

        Keyword Args:
            cachedir: Directory for cached python objects. :any:`AnyCache`
                      instances on the same `cachedir` share the same cache.
            maxsize: Maximum cache size in bytes.
                     `None` does not limit the cache size.
                     `0` disables caching.
                     It the maximum size is smaller than the last cached
                     object, this object is kept.
                     During object write the cache size might be larger than
                     `maxsize`. At maximum twice as large as the maximum object
                     size.
            debug: Send detailed cache read/write information to :any:`logging`.

        The :any:`AnyCache` instance mainly serves the :any:`AnyCache.anycache`
        method for caching the result of functions.

        >>> from anycache import AnyCache
        >>> ac = AnyCache()
        >>> @ac.anycache()
        ... def myfunc(posarg, kwarg=3):
        ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
        ...     return posarg + kwarg
        >>> myfunc(4, 5)
          Calcing 4 + 5 = 9
        9
        >>> myfunc(4, 5)
        9
        >>> myfunc(4, 2)
          Calcing 4 + 2 = 6
        6

        The cache size is returned by :any:`AnyCache.size`.

        >>> ac.size
        10

        The cache size can be limited via `maxsize`.
        A `maxsize` of `0` disables caching.

        >>> ac.maxsize = 0
        >>> myfunc(4, 5)
          Calcing 4 + 5 = 9
        9

        The cache is preserved in this case, and needs to be cleared explicitly:

        >>> ac.size
        10
        >>> ac.clear()
        >>> ac.size
        0
        """
        self.cachedir = cachedir
        self.maxsize = maxsize
        self.debug = debug

    @property
    def cachedir(self):
        """
        Cache directory use for all cache files.

        :any:`AnyCache` instances on the same `cachedir` share the same cache.
        """
        if self.__cachedir is None:
            self.__cachedir = pathlib.Path(tempfile.mkdtemp(suffix='.anycache'))
        return self.__cachedir

    @cachedir.setter
    def cachedir(self, cachedir):
        if cachedir is not None:
            self.__cachedir = pathlib.Path(cachedir)
            self.__explicit_cachedir = True
        else:
            self.__cachedir = None
            self.__explicit_cachedir = False

    def __del__(self):
        if not self.__explicit_cachedir:
            self.clear()

    def anycache(self, depfilefunc=None, debug=False):
        """
        Decorator to cache result of function depending on arguments.

        Keyword Args:
            depfilefunc: Dependency file function (see example below)
            debug (bool): Send detailed cache read/write information to :any:`logging`.

        >>> from anycache import AnyCache
        >>> ac = AnyCache()
        >>> @ac.anycache()
        ... def myfunc(posarg, kwarg=3):
        ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
        ...     return posarg + kwarg
        >>> myfunc(2, 5)
          Calcing 2 + 5 = 7
        7
        >>> myfunc(2, 5)
        7

        File I/O is not tracked by the decorator.
        Instead a function needs to be implemented, which returns the paths
        of the files, which influence the function result.
        The `depfilefunc` is called with the function result and all arguments.
        The following example, depends on the path of the source code itself:

        >>> def mydepfilefunc(result, posarg, kwarg=3):
        ...     print("  Deps of %r + %r = %r" % (posarg, kwarg, result))
        ...     return [__file__]
        >>> @ac.anycache(depfilefunc=mydepfilefunc)
        ... def myfunc(posarg, kwarg=3):
        ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
        ...     return posarg + kwarg
        >>> myfunc(2, 7)
          Calcing 2 + 7 = 9
          Deps of 2 + 7 = 9
        9
        """
        _debug = debug

        def decorator(func):

            def wrapped(*args, **kwargs):
                if self.maxsize == 0:
                    result = func(*args, **kwargs)
                else:
                    funcinfo = _FuncInfo(func, args, kwargs, depfilefunc)
                    result = self._anycache(funcinfo, _debug)
                return result

            return wrapped
        return decorator

    def clear(self):
        """Clear the cache by removing all cache files."""
        cachedir = self.cachedir
        self._get_debugout()("CLEARING cache")
        if cachedir.exists():
            for file in cachedir.glob("*"):
                file.unlink()
            cachedir.rmdir()

    @property
    def size(self):
        """Return total size of all cache files."""
        if self.cachedir.exists():
            size = sum([file.stat().st_size for file in self.cachedir.glob("*")])
        else:
            size = 0
        return size

    def _anycache(self, funcinfo, debug):
        debugout = self._get_debugout(debug)
        ident = self._get_ident(funcinfo)
        ce = _CacheInfo.create_ce_from_ident(self.cachedir, ident)
        self._ensure_cachedir()
        # try to read
        valid, result = AnyCache._read(ce, debugout)
        if valid:
            ce.data.touch()
        else:
            func, args, kwargs, depfilefunc = funcinfo
            # execute
            result = func(*args, **kwargs)
            # deps
            deps = tuple(depfilefunc(result, *args, **kwargs)) if depfilefunc else []
            # write
            AnyCache._write(ce, result, deps, debugout)
            # remove old
            AnyCache._tidyup(self.cachedir, self.maxsize, debugout)
        return result

    def _get_debugout(self, debug=False):
        if self.debug or debug:
            return logging.getLogger(__name__).debug
        else:
            def null(msg):
                pass
            return null

    @staticmethod
    def _get_ident(fi):
        func = fi.func
        name = "%s.%s(%s, %s)" % (func.__module__, func.__name__, fi.args, fi.kwargs)
        h = hashlib.sha256()
        h.update(_bytes(name))
        ident = h.hexdigest()
        return ident

    def _ensure_cachedir(self):
        if not self.cachedir.exists():
            self.cachedir.mkdir(parents=True)

    @staticmethod
    def _is_outdated(ce, debugout):
        outdated = True
        if ce.dep.exists() and ce.data.exists():
            data_mtime = ce.data.stat().st_mtime
            try:
                with open(str(ce.dep), "r") as depfile:
                    outdated = any([(pathlib.Path(line.rstrip()).stat().st_mtime > data_mtime)
                                    for line in depfile])
            except Exception:
                debugout("CORRUPT cache dep '%s'" % (ce.ident))
        return outdated

    @staticmethod
    def _read(ce, debugout):
        valid, result = False, None
        if not AnyCache._is_outdated(ce, debugout):
            with open(str(ce.data), "rb") as cachefile:
                try:
                    result, valid = pickle.load(cachefile), True
                    debugout("READING cache entry '%s'" % (ce.ident))
                except Exception:
                    debugout("CORRUPT cache entry '%s'" % (ce.ident))
        return valid, result

    @staticmethod
    def _write(ce, result, deps, debugout):
        with open(str(ce.data), "wb") as cachefile:
            debugout("WRITING cache entry '%s'" % (ce.ident))
            pickle.dump(result, cachefile)
        with open(str(ce.dep), "w") as depfile:
            for dep in deps:
                depfile.write("%s\n" % (dep))

    @staticmethod
    def _tidyup(cachedir, maxsize, debugout):
        if maxsize is not None:
            cacheinfo = _CacheInfo(cachedir)
            totalsize = cacheinfo.totalsize
            ceis = collections.deque(sorted(cacheinfo.cacheentryinfos, key=lambda info: info.mtime))
            while (totalsize > maxsize) and (len(ceis) > 2):
                oldest = ceis.popleft()
                totalsize -= oldest.size
                oldest.ce.data.unlink()
                oldest.ce.dep.unlink()
                debugout("REMOVING cache entry '%s'" % (oldest.ce.ident))


DEFAULT_CACHE = AnyCache()


def anycache(depfilefunc=None, debug=False, cachedir=None, maxsize=None):
    """
    Decorator to cache result of function depending on arguments.

    This decorator uses one unlimited global cache within one python run.
    Different anycached functions have different cache name spaces and do
    not influence each other.

    To preserve the cache result between multiple python runs, use
    an :any:`AnyCache` instance with a persistent `cachedir`.

    Keyword Args:
        depfilefunc: Dependency file function (see example below)
        debug (bool): Send detailed cache read/write information to :any:`logging`.
        cachedir: Directory for cached python objects. :any:`AnyCache`
                  instances on the same `cachedir` share the same cache.
        maxsize: Maximum cache size in bytes.
                 `None` does not limit the cache size.
                 `0` disables caching.
                 It the maximum size is smaller than the last cached
                 object, this object is kept.
                 During object write the cache size might be larger than
                 `maxsize`. At maximum twice as large as the maximum object
                 size.

    >>> from anycache import anycache
    >>> @anycache()
    ... def myfunc(posarg, kwarg=3):
    ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
    ...     return posarg + kwarg
    >>> myfunc(2, 5)
      Calcing 2 + 5 = 7
    7
    >>> myfunc(2, 5)
    7

    File I/O is not tracked by the decorator.
    Instead a function needs to be implemented, which returns the paths
    of the files, which influence the function result.
    The `depfilefunc` is called with the function result and all arguments.
    The following example, depends on the path of the source code itself:

    >>> def mydepfilefunc(result, posarg, kwarg=3):
    ...     print("  Deps of %r + %r = %r" % (posarg, kwarg, result))
    ...     return [__file__]
    >>> @anycache(depfilefunc=mydepfilefunc)
    ... def myfunc(posarg, kwarg=3):
    ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
    ...     return posarg + kwarg
    >>> myfunc(2, 7)
      Calcing 2 + 7 = 9
      Deps of 2 + 7 = 9
    9
    """
    if (cachedir is not None) or (maxsize is not None):
        ac = AnyCache(cachedir=cachedir, maxsize=maxsize)
    else:
        ac = DEFAULT_CACHE
    return ac.anycache(depfilefunc=depfilefunc, debug=debug)

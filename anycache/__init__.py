"""Cache any python object to file."""

import collections
import hashlib
import logging
import pathlib
import shutil
import sys
import tempfile

import dill as pickle  # improved pickle
import filelock

__version__ = "2.0.6"
__author__ = "c0fec0de"
__author_email__ = "c0fec0de@gmail.com"
__description__ = """Cache any python object to file using improved pickling ."""
__url__ = "https://github.com/c0fec0de/anycache"


__all__ = ("AnyCache", "anycache", "get_defaultcache")

_CacheEntry = collections.namedtuple("_CacheEntry", ("ident", "data", "dep", "lock"))
_CacheEntryInfo = collections.namedtuple("_CacheEntryInfo", ("ce", "mtime", "size"))
_FuncInfo = collections.namedtuple("FuncInfo", ("func", "args", "kwargs", "depfilefunc"))

if sys.version_info[0] < 3:  # pragma: no cover
    _bytes = bytes
    FileExistsError = OSError
else:  # pragma: no cover
    def _bytes(name):
        return bytes(name, encoding='utf-8')

_CACHE_SUFFIX = ".cache"
_DEP_SUFFIX = ".dep"
_LOCK_SUFFIX = ".lock"


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
        lock = filelock.FileLock(str(cachedir / (ident + _LOCK_SUFFIX)))
        return _CacheEntry(ident, data, dep, lock)

    @staticmethod
    def create_ce_from_datafilepath(datafilepath):
        ident = datafilepath.name
        data = datafilepath
        dep = datafilepath.with_suffix(_DEP_SUFFIX)
        lock = filelock.FileLock(str(datafilepath.with_suffix(_LOCK_SUFFIX)))
        return _CacheEntry(ident, data, dep, lock)

    @staticmethod
    def create_cei(ce):
        mtime = ce.data.stat().st_mtime
        size = ce.data.stat().st_size + ce.dep.stat().st_size
        return _CacheEntryInfo(ce, mtime, size)


class AnyCache(object):

    def __init__(self, cachedir=None, maxsize=None):
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

    def anycache(self, depfilefunc=None):
        """
        Decorator to cache result of function depending on arguments.

        Keyword Args:
            depfilefunc: Dependency file function (see example below)

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
        def decorator(func):

            def is_outdated(*args, **kwargs):
                funcinfo = _FuncInfo(func, args, kwargs, depfilefunc)
                return self._is_outdated(funcinfo)

            def remove(*args, **kwargs):
                funcinfo = _FuncInfo(func, args, kwargs, depfilefunc)
                return self._remove(funcinfo)

            def get_ident(*args, **kwargs):
                funcinfo = _FuncInfo(func, args, kwargs, depfilefunc)
                return self._get_ident(funcinfo)

            def wrapped(*args, **kwargs):
                if self.maxsize == 0:
                    result = func(*args, **kwargs)
                else:
                    funcinfo = _FuncInfo(func, args, kwargs, depfilefunc)
                    result = self._anycache(funcinfo)
                return result

            wrapped.is_outdated = is_outdated
            wrapped.remove = remove
            wrapped.get_ident = get_ident

            return wrapped
        return decorator

    def is_outdated(self, func, *args, **kwargs):
        """
        Return `True` if cache is outdated for `func` used with `args` and `kwargs`.

        >>> from anycache import AnyCache
        >>> ac = AnyCache()
        >>> @ac.anycache()
        ... def myfunc(posarg, kwarg=3):
        ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
        ...     return posarg + kwarg
        >>> ac.is_outdated(myfunc, 2, 5)
        True
        >>> myfunc(2, 5)
          Calcing 2 + 5 = 7
        7
        >>> ac.is_outdated(myfunc, 2, 5)
        False
        """
        return func.is_outdated(*args, **kwargs)

    def remove(self, func, *args, **kwargs):
        """
        Remove cache data for `func` used with `args` and `kwargs`.

        >>> from anycache import AnyCache
        >>> ac = AnyCache()
        >>> @ac.anycache()
        ... def myfunc(posarg, kwarg=3):
        ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
        ...     return posarg + kwarg
        >>> myfunc(2, 5)
          Calcing 2 + 5 = 7
        7
        >>> ac.remove(myfunc, 2, 5)
        >>> myfunc(2, 5)
          Calcing 2 + 5 = 7
        7

        Removing non-existing cache entries is not an error:

        >>> ac.remove(myfunc, 2, 5)
        >>> ac.remove(myfunc, 2, 5)
        """
        return func.remove(*args, **kwargs)

    def get_ident(self, func, *args, **kwargs):
        """
        Return identification string for `func` used with `args` and `kwargs`.

        >>> from anycache import AnyCache
        >>> ac = AnyCache()
        >>> @ac.anycache()
        ... def myfunc(posarg, kwarg=3):
        ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
        ...     return posarg + kwarg
        >>> @ac.anycache()
        ... def otherfunc(posarg, kwarg=3):
        ...     print("  Calcing %r + %r = %r" % (posarg, kwarg, posarg + kwarg))
        ...     return posarg + kwarg
        >>> ac.get_ident(myfunc, 2, 5)
        '19044d3869955fa79d7f3db8fcdc5af84b3f55c0bdab2b4aee1bb21e1a9856c9'
        >>> ac.get_ident(myfunc, 2, 6)
        '1885e09f9898a1f1bd186f052d0e810693faa14b70e7b6b22de61b90c8171427'
        >>> ac.get_ident(otherfunc, 2, 5)
        '9b8aea26422999aaa7aed0fdb4d5145fd33b87de20f322cf175997e9b1835158'
        """
        return func.get_ident(*args, **kwargs)

    def clear(self):
        """Clear the cache by removing all cache files."""
        # destructor save implementation
        try:
            cachedir = self.__cachedir
        except AttributeError:  # pragma: no cover
            cachedir = None
        if cachedir and cachedir.exists():
            if logging:  # pragma: no cover
                logging.getLogger(__name__).debug("CLEARING cache '%s" % cachedir)
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

    def _anycache(self, funcinfo):
        logger = logging.getLogger(__name__)
        ident = self._get_ident(funcinfo)
        ce = _CacheInfo.create_ce_from_ident(self.cachedir, ident)
        self._ensure_cachedir()
        # try to read
        valid, result = AnyCache.__read(logger, ce)
        if not valid:
            func, args, kwargs, depfilefunc = funcinfo
            # execute
            result = func(*args, **kwargs)
            # deps
            deps = tuple(depfilefunc(result, *args, **kwargs)) if depfilefunc else []
            # write
            AnyCache.__write(logger, ce, result, deps)
            # remove old
            AnyCache.__tidyup(logger, self.cachedir, self.maxsize)
        return result

    def _is_outdated(self, funcinfo):
        logger = logging.getLogger(__name__)
        ident = self._get_ident(funcinfo)
        ce = _CacheInfo.create_ce_from_ident(self.cachedir, ident)
        self._ensure_cachedir()
        with ce.lock:
            is_outdated = AnyCache.__is_outdated(logger, ce)
        return is_outdated

    def _remove(self, funcinfo):
        logger = logging.getLogger(__name__)
        ident = self._get_ident(funcinfo)
        ce = _CacheInfo.create_ce_from_ident(self.cachedir, ident)
        self._ensure_cachedir()
        AnyCache.__remove(logger, ce)

    @staticmethod
    def _get_ident(fi):
        func = fi.func
        name = "%s.%s(%s, %s)" % (func.__module__, func.__name__, fi.args, fi.kwargs)
        h = hashlib.sha256()
        h.update(_bytes(name))
        ident = h.hexdigest()
        return ident

    def _ensure_cachedir(self):
        try:
            self.cachedir.mkdir(parents=True)
        except FileExistsError:
            pass

    @staticmethod
    def __is_outdated(logger, ce):
        outdated = True
        if ce.dep.exists() and ce.data.exists():
            data_mtime = ce.data.stat().st_mtime
            try:
                with open(str(ce.dep), "r") as depfile:
                    outdated = any([(pathlib.Path(line.rstrip()).stat().st_mtime > data_mtime)
                                    for line in depfile])
            except Exception:
                logger.warn("CORRUPT cache dep '%s'" % (ce.dep))
        return outdated

    @staticmethod
    def __read(logger, ce):
        valid, result = False, None
        with ce.lock:
            if not AnyCache.__is_outdated(logger, ce):
                with open(str(ce.data), "rb") as cachefile:
                    try:
                        result, valid = pickle.load(cachefile), True
                        logger.info("READING cache entry '%s'" % (ce.ident))
                    except Exception as exc:
                        logger.warn("CORRUPT cache entry '%s'. %r" % (ce.data, exc))
                ce.data.touch()
        return valid, result

    @staticmethod
    def __write(logger, ce, result, deps):
        logger.info("WRITING cache entry '%s'" % (ce.ident))
        # we need to lock the cache for write
        # writing takes a long time, so we are writing to temporay files, lock and copy over.
        try:
            with tempfile.NamedTemporaryFile("wb", prefix="anycache-", suffix=_CACHE_SUFFIX) as datatmpfile:
                with tempfile.NamedTemporaryFile("w", prefix="anycache-", suffix=_DEP_SUFFIX) as deptmpfile:
                    # data
                    pickle.dump(result, datatmpfile)
                    datatmpfile.flush()
                    # dep
                    for dep in deps:
                        deptmpfile.write("%s\n" % (dep))
                    deptmpfile.flush()
                    # copy over
                    with ce.lock:
                        shutil.copyfile(datatmpfile.name, str(ce.data))
                        shutil.copyfile(deptmpfile.name, str(ce.dep))
        except Exception as exc:  # pragma: no cover
            logger.warn("FAILED cache write '%s'. %r" % (ce.data, exc))

    @staticmethod
    def __tidyup(logger, cachedir, maxsize):
        if maxsize is not None:
            cacheinfo = _CacheInfo(cachedir)
            totalsize = cacheinfo.totalsize
            ceis = collections.deque(sorted(cacheinfo.cacheentryinfos, key=lambda info: info.mtime))
            while (totalsize > maxsize) and (len(ceis) > 2):
                cei = ceis.popleft()
                totalsize -= cei.size
                AnyCache.__remove(logger, cei.ce)

    @staticmethod
    def __remove(logger, ce):
        with ce.lock:
            if ce.data.exists():
                ce.data.unlink()
            if ce.dep.exists():
                ce.dep.unlink()
        logger.info("REMOVING cache entry '%s'" % (ce.ident))


__DEFAULT_CACHE = None


def anycache(cachedir=None, maxsize=None, depfilefunc=None):
    """
    Decorator to cache result of function depending on arguments.

    This decorator uses one unlimited global cache within one python run.
    Different anycached functions have different cache name spaces and do
    not influence each other.

    To preserve the cache result between multiple python runs, use
    an :any:`AnyCache` instance with a persistent `cachedir`.

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
        depfilefunc: Dependency file function (see example below)

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
        ac = get_defaultcache()

    return ac.anycache(depfilefunc=depfilefunc)


def get_defaultcache():
    """Return unlimited default :any:`AnyCache` instance."""
    global __DEFAULT_CACHE
    if __DEFAULT_CACHE is None:
        __DEFAULT_CACHE = AnyCache()
    return __DEFAULT_CACHE

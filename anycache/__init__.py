"""Cache any python object to file."""
import collections
import hashlib
import inspect
import logging
import pathlib
import tempfile

import dill as pickle  # improved pickle

__version__ = "0.0.dev1"
__author__ = "c0fec0de"
__author_email__ = "c0fec0de@gmail.com"
__description__ = """Cache any python object to file using improved pickling ."""
__url__ = "https://github.com/c0fec0de/anycache"


_CacheEntry = collections.namedtuple("_CacheEntry", ("ident", "data", "dep"))
_CacheEntryInfo = collections.namedtuple("_CacheEntryInfo", ("ce", "mtime", "size"))
_FuncInfo = collections.namedtuple("FuncInfo", ("func", "args", "kwargs", "depfilefunc"))


class _CacheInfo(object):

    def __init__(self, cachedir):
        datafilepaths = cachedir.glob("*%s" % AnyCache._DATA_SUFFIX)
        self.cacheentries = [_CacheInfo.create_ce_from_datafilepath(d) for d in datafilepaths]
        self.cacheentryinfos = [_CacheInfo.create_cei(ce) for ce in self.cacheentries]
        self.totalsize = sum([cei.size for cei in self.cacheentryinfos])

    @staticmethod
    def create_ce_from_ident(cachedir, ident):
        data = cachedir / (ident + AnyCache._DATA_SUFFIX)
        dep = cachedir / (ident + AnyCache._DEP_SUFFIX)
        return _CacheEntry(ident, data, dep)

    @staticmethod
    def create_ce_from_datafilepath(datafilepath):
        ident = datafilepath.name
        data = datafilepath
        dep = datafilepath.with_suffix(AnyCache._DEP_SUFFIX)
        return _CacheEntry(ident, data, dep)

    @staticmethod
    def create_cei(ce):
        mtime = ce.data.stat().st_mtime
        size = ce.data.stat().st_size + ce.dep.stat().st_size
        return _CacheEntryInfo(ce, mtime, size)


class AnyCache(object):

    _DATA_SUFFIX = ".cache"
    _DEP_SUFFIX = ".dep"

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

    def decorate(self, depfilefunc=None, debug=False):
        _debug = debug

        def decorator(func):
            """Wrap function `func`."""

            def wrapped(*args, **kwargs):
                maxsize = self.maxsize

                if maxsize == 0:
                    result = func(*args, **kwargs)
                else:
                    funcinfo = _FuncInfo(func, args, kwargs, depfilefunc)
                    result = self._decorate(funcinfo, _debug)
                return result

            return wrapped
        return decorator

    def clear(self):
        """Clear the cache by removing all cache files."""
        cachedir = self.cachedir
        if cachedir.exists():
            for file in cachedir.glob("*"):
                file.unlink()
            cachedir.rmdir()
        self._get_debugout()("CLEARING cache")

    @property
    def size(self):
        """Return total size of all cache files."""
        if self.cachedir.exists():
            size = sum([file.stat().st_size for file in self.cachedir.glob("*")])
        else:
            size = 0
        return size

    def _decorate(self, funcinfo, debug):
        func, args, kwargs, depfilefunc = funcinfo
        debugout = self._get_debugout(debug)
        self._ensure_cachedir()
        ident = self._get_ident(func, *args, **kwargs)
        ce = _CacheInfo.create_ce_from_ident(self.cachedir, ident)
        # read
        valid, result = AnyCache._read(ce, debugout)
        if valid:
            ce.data.touch()
        else:
            # execute
            result = func(*args, **kwargs)
            # deps
            deps = list(depfilefunc(result, *args, **kwargs)) if depfilefunc else []
            deps.append(inspect.getfile(func))
            # write
            AnyCache._write(ce, result, deps, debugout)
            # remove old
            AnyCache._tidyup(self.cachedir, self.maxsize, debugout)
        return result

    def _get_debugout(self, debug=False):
        if self.debug or debug:
            return logging.getLogger(__name__).warn
        else:
            return AnyCache.__devnull

    @staticmethod
    def __devnull(msg):
        pass

    @staticmethod
    def _get_ident(func, *args, **kwargs):
        name = "%s.%s(%s, %s)" % (func.__module__, func.__name__, args, kwargs)
        h = hashlib.sha256()
        h.update(bytes(name, encoding="utf-8"))
        ident = h.hexdigest()
        return ident

    def _ensure_cachedir(self):
        if not self.cachedir.exists():
            self.cachedir.mkdir(parents=True)

    @staticmethod
    def _read(ce, debugout):
        valid, result = False, None
        outdated = True
        if ce.dep.exists() and ce.data.exists():
            data_mtime = ce.data.stat().st_mtime
            with open(str(ce.dep), "r") as depfile:
                outdated = any([(pathlib.Path(line.rstrip()).stat().st_mtime > data_mtime)
                                for line in depfile])
        if not outdated:
            with open(str(ce.data), "rb") as cachefile:
                result, valid = pickle.load(cachefile), True
                debugout("READING cache entry '%s'" % (ce.ident))
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


def anycache(depfilefunc=None, debug=False):
    return DEFAULT_CACHE.decorate(depfilefunc=depfilefunc, debug=debug)

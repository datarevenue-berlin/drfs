import urllib.parse
import warnings
from pathlib import Path, PurePath

from urlpath import URL, cached_property

from drfs import config
from drfs.filesystems import FILESYSTEMS, get_fs

# Actual type of Path depends on the OS and is determined on instantiation.
PATH_CLASS = type(Path())


# noinspection PyUnresolvedReferences
class DRPathMixin:
    @property
    def is_template(self):
        s = str(self)
        return 0 <= s.find("{") < s.find("}")

    @property
    def is_wildcard(self):
        return "*" in str(self)

    @property
    def flag(self):
        return self / "_SUCCESS"

    def format(self, *args, **kwargs):
        return DRPath(str(self).format(*args, **kwargs))

    @property
    def storage_options(self):
        try:
            opts = self._storage_options
        except AttributeError as e:
            warnings.warn(str(e))
            return None
        if opts is not None:
            return opts
        config_scheme_key = self.scheme if self.scheme else "file"
        return config["fs_opts"][config_scheme_key].get(dict)

    def startswith(self, *args, **kwargs):
        """Act like a string - for compatibility with s3fs.put"""
        return str(self).startswith(*args, **kwargs)

    def __getitem__(self, item):
        """Act like a string - for compatibility with s3fs.put"""
        return str(self)[item]

    opts = storage_options


class RemotePath(URL, DRPathMixin):
    """
    A very pathlib.Path version for RemotePaths.

    If you use a method that requires an underlying filesystem to
    be instantiated (such as `open`), storage_options may be needed (to provide
    credentials etc.). They are taken from settings.FS_OPTS by default,
    but you can also set them by providing `storage_options` kwarg on path
    instantiation.
    """

    def __new__(cls, *args, storage_options=None, **kwargs):
        self = cls._from_parts(args, init=False)
        self._init()
        self._storage_options = storage_options
        return self

    def _init(self):
        super()._init()
        self._acc_real = None

    @property
    def _accessor(self):
        if self._acc_real is None:
            try:
                self._acc_real = FILESYSTEMS[self.scheme](**self.opts)
            except KeyError:
                raise ValueError(
                    "Scheme {} not found in available filesystems"
                    ", try installing it.".format(self.scheme)
                )
        return self._acc_real

    def exists(self):
        return self._accessor.exists(str(self))

    def open(self, *args, **kwargs):
        """Return a File object dependent of remote storage used."""
        return self._accessor.open(str(self), *args, **kwargs)

    def unlink(self):
        self._accessor.remove(str(self))

    def iterdir(self):
        """Iterate over the files in this directory.

        Returns
        -------
        files: list

        Warnings:
        ---------
            Instead of relative paths this will return absolute paths
            to the files in the directory.
        """
        for path in self._accessor.ls(str(self)):
            yield path

    def mkdir(self, *args, **kwargs):
        """NOP for remote paths."""
        pass

    @property
    @cached_property
    def path(self):
        """The path of url, it's with trailing sep.

        We're overriding this to add {}% to safe_pchars. This enables
        RemotePath to not mess up template paths.
        """

        # https://tools.ietf.org/html/rfc3986#appendix-A
        safe_pchars = "-._~!$&'()*+,;=:@{}%"

        begin = 1 if self._drv or self._root else 0

        return (
            self._root
            + self._flavour.sep.join(
                urllib.parse.quote(i, safe=safe_pchars)
                for i in self._parts[begin:-1] + [self.name]
            )
            + self.trailing_sep
        )

    def _make_child(self, args):
        res = super()._make_child(args)
        res._storage_options = self._storage_options
        res._acc_real = self._acc_real
        return res


class LocalPath(PATH_CLASS, DRPathMixin):
    pass


class DRPath:
    def __new__(cls, path, *args, **kwargs):
        if cls is DRPath:
            if get_fs(path, rtype="class").is_remote:
                cls = RemotePath
            else:
                cls = LocalPath
        obj = cls(path, *args, **kwargs)
        return obj


def asstr(arg):
    """Convert arg into its string representation.

    This is only done if arg is subclass of PurePath
    """
    if issubclass(type(arg), PurePath):
        return str(arg)
    return arg


def aspath(x):
    if isinstance(x, DRPathMixin):
        return x
    if isinstance(x, (list, tuple, set)):
        if len(x) == 0:
            return x
        return type(x)(map(DRPath, x))  # return the same type of iterable
    else:
        return DRPath(x)


def _get_path_class(path):
    if get_fs(path).is_remote:
        return RemotePath
    else:
        return Path

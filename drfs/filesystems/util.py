import urllib.parse
from functools import partial, wraps
from pathlib import Path

from drfs import settings
from drfs.util import prepend_scheme, remove_scheme


def get_fs(path, opts=None, rtype="instance"):
    """Helper to infer filesystem correctly.

    Gets filesystem options from settings and updates them with given `opts`.

    Parameters
    ----------
    path: str
        Path for which we want to infer filesystem.
    opts: dict
        Kwargs that will be passed to inferred filesystem instance.
    rtype: str
        Either 'instance' (default) or 'class'.
    """
    from drfs.filesystems import FILESYSTEMS

    try:
        protocol = path.scheme
    except AttributeError:
        protocol = urllib.parse.urlparse(str(path)).scheme

    try:
        cls = FILESYSTEMS[protocol]
        if rtype == "class":
            return cls
    except KeyError:
        raise KeyError(
            f"No filesystem for protocol {protocol}. Try "
            f"installing it. Available protocols are: "
            f"{set(FILESYSTEMS.keys())}"
        )
    opts_ = getattr(settings, "FS_OPTS", {}).copy()  # type: dict
    if opts is not None:
        opts_.update(opts)
    opts_ = _fix_opts_abfs(cls, path, opts_)
    return cls(**opts_)


def _fix_opts_abfs(cls, path, opts: dict):
    try:
        from drfs.filesystems.azure_blob import AzureBlobFileSystem, extract_abfs_parts
    except ImportError:
        AzureBlobFileSystem = extract_abfs_parts = None

    if (
        AzureBlobFileSystem is not None
        and cls is AzureBlobFileSystem
        and "account_name" not in opts
    ):
        opts = opts.copy()
        opts["account_name"] = extract_abfs_parts(path)[0]
    return opts


def allow_pathlib(func):
    """Allow methods to receive pathlib.Path objects.

    Parameters
    ----------
    func: callable
        function to decorate must have the following signature
        self, path, *args, **kwargs

    Returns
    -------
    wrapper: callable
    """

    @wraps(func)
    def wrapper(self, path, *args, **kwargs):
        # Can only be used if path is passed as first argument right
        # after self
        from drfs.path import asstr

        p = asstr(path)
        return func(self, p, *args, **kwargs)

    return wrapper


def return_pathlib(func):
    @wraps(func)
    def wrapper(self, path, *args, **kwargs):
        from drfs.path import aspath

        res = func(self, path, *args, **kwargs)
        if all(isinstance(item, tuple) for item in res):
            as_path = [(aspath(item[0]),) + item[1:] for item in res]
        else:
            as_path = aspath(res)
        return as_path

    return wrapper


def return_schemes(func):
    """Make sure method returns full path with scheme."""

    @wraps(func)
    def wrapper(self, path, *args, **kwargs):
        res = func(self, path, *args, **kwargs)
        try:
            res = list(map(partial(prepend_scheme, self.scheme), res))
        except TypeError:
            res = prepend_scheme(self.scheme, res)
        return res

    return wrapper


def maybe_remove_scheme(func):
    """Remove scheme from args and kwargs in case underlying fs does not support it."""

    @wraps(func)
    def wrapper(self, path, *args, **kwargs):
        if not self.supports_scheme:
            path = remove_scheme(path, raise_=False)
            args = [remove_scheme(a, raise_=False) for a in args]
            kwargs = {
                k: remove_scheme(v, raise_=False) if isinstance(v, (Path, str)) else v
                for k, v in kwargs.items()
            }

        return func(self, path, *args, **kwargs)

    return wrapper

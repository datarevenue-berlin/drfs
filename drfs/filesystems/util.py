import urllib.parse
from functools import partial, wraps
from pathlib import Path

from drfs import config
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
        protocol = _get_protocol(path)

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
    config_scheme_key = protocol if protocol else "file"
    opts_ = config["fs_opts"][config_scheme_key].get(dict).copy()  # type: dict
    if opts is not None:
        opts_.update(opts)
    opts_ = _fix_opts_abfs(cls, path, opts_)
    return cls(**opts_)


def _get_protocol(path):
    if "://" in str(path):
        protocol = urllib.parse.urlparse(str(path)).scheme
    else:
        # most likely a windows path, basically if in doubt assume local
        protocol = ""
    return protocol


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

"""FileSystem abstraction.

Often we don't want to care about where the files are stored. Dealing with
different filesystems or storage providers is often repetitive and boring.
Therefore the aim of this module is to provide a generalized interface for
filesystems that comply with luigi's requirements for FileSystem classes
as well as dask's requirements.

This module also provides a implementation of a LocalFileSystem which is useful
for tests and/or smaller projects that can be developed locally.

Currently methods that are required to be implemented are:
- open
- exists
- ls
- remove
- mv (file -> file)
- makedirs
- rmdir
- info -> {"LastModified": dt.datetime}

Which filesystem to use is usually inferred from the path/protocol.
"""
import builtins
import datetime
import os
import shutil
import urllib.parse
from functools import partial, wraps
from glob import glob as glob_

import pytz

from . import settings
from .util import prepend_scheme

try:
    import gcsfs
except ImportError:
    gcsfs = None

try:
    import s3fs
except ImportError:
    s3fs = None

try:
    import azureblobfs.dask as abfs
except ImportError:
    abfs = None


FILESYSTEMS = {}


# TODO: should work for functions and methods (see dask's delay)
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


# TODO: should work for functions and methods
def return_pathlib(func):
    @wraps(func)
    def wrapper(self, path, *args, **kwargs):
        from drfs.path import aspath
        res = func(self, path, *args, **kwargs)
        as_path = aspath(res)
        return as_path
    return wrapper


# TODO: should work for functions and methods
def handle_schemes(func):
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


# region Base
class FileSystemBase:

    fs_cls = None  # type: type
    scheme = None  # type: str
    is_remote = None  # type: bool

    def __init__(self, *args, **kwargs):
        if self.fs_cls is None:
            # Sometimes, like in LocalFileSystem, we don't need underlying fs
            self.fs = None
        else:
            self.fs = self.fs_cls(*args, **kwargs)

    @allow_pathlib
    def open(self, path, *args, **kwargs):
        return self.fs.open(path, *args, **kwargs)

    @allow_pathlib
    def exists(self, path, *args, **kwargs):
        return self.fs.exists(path, *args, **kwargs)

    @return_pathlib
    @handle_schemes
    @allow_pathlib
    def ls(self, path, *args, **kwargs):
        return self.fs.ls(path, *args, **kwargs)

    @allow_pathlib
    def remove(self, path, *args, **kwargs):
        try:
            return self.fs.remove(path, *args, **kwargs)
        except AttributeError:
            return self.fs.rm(path, *args, **kwargs)

    @allow_pathlib
    def copy(self, path, *args, **kwargs):
        try:
            return self.fs.copy(path, *args, **kwargs)
        except AttributeError:
            return self.fs.cp(path, *args, **kwargs)

    @allow_pathlib
    def mv(self, path, *args, **kwargs):
        return self.fs.mv(path, *args, **kwargs)

    @allow_pathlib
    def makedirs(self, path, *args, **kwargs):
        return self.fs.makedirs(path, *args, **kwargs)

    @allow_pathlib
    def rmdir(self, path, *args, **kwargs):
        return self.fs.rmdir(path, *args, **kwargs)

    @allow_pathlib
    def info(self, path, *args, **kwargs):
        return self.fs.info(path, *args, **kwargs)

    @return_pathlib
    @handle_schemes
    @allow_pathlib
    def walk(self, *args, **kwargs):
        return self.fs.walk(*args, **kwargs)

    @return_pathlib
    @handle_schemes
    @allow_pathlib
    def glob(self, *args, **kwargs):
        return self.fs.glob(*args, **kwargs)

    def cp(self, *args, **kwargs):
        """cp is an alias for copy"""
        return self.copy(*args, **kwargs)

    def rm(self, *args, **kwargs):
        """rm is an alias for remove"""
        return self.remove(*args, **kwargs)
# endregion


# region Local
class LocalFileSystem(FileSystemBase):
    """Emulates a remote filesystem on the local disk."""

    fs_cls = None  # we could do even without subclassing FSBase
    scheme = ''
    is_remote = False

    @allow_pathlib
    def open(self, path, *args, **kwargs):
        """Open a file."""
        self._makedirs_parent(path)
        return builtins.open(path, *args, **kwargs)

    @allow_pathlib
    def exists(self, path):
        """Return True if file exists."""
        return os.path.exists(path)

    @allow_pathlib
    def _makedirs_parent(self, path):
        dir_ = os.path.dirname(path)
        os.makedirs(dir_, exist_ok=1)

    @allow_pathlib
    def makedirs(self, *args, **kwargs):
        os.makedirs(*args, **kwargs)

    @allow_pathlib
    def remove(self, path):
        """Remove a file."""
        os.remove(path)

    @return_pathlib
    @allow_pathlib
    def ls(self, path):
        """List directory."""
        return list(map(lambda x: os.path.join(path, x), os.listdir(path)))

    @allow_pathlib
    def mv(self, src, dst):
        """Move file or directory. Source parent dir will be created."""
        self._makedirs_parent(dst)
        shutil.move(src, dst)

    @allow_pathlib
    def rmdir(self, path):
        """Remove directory."""
        os.rmdir(path)

    @allow_pathlib
    def info(self, path):
        """Get a dict with only LastModified time in UTC."""
        mtime = os.path.getmtime(path)
        return {
            'LastModified': datetime.datetime.fromtimestamp(mtime, pytz.UTC)
        }

    @return_pathlib
    @allow_pathlib
    def walk(self, path):
        """Walk over all files in this directory (recursively)."""
        return [os.path.join(root, f)
                for root, dirs, files in os.walk(path)
                for f in files]

    @return_pathlib
    @allow_pathlib
    def glob(self, path):
        """Find files by glob-matching."""
        return glob_(path)

    @allow_pathlib
    def touch(self, path):
        self.open(path, 'w').close()


FILESYSTEMS[''] = LocalFileSystem
FILESYSTEMS['file'] = LocalFileSystem
# endregion


# region GCS
if gcsfs is not None:
    class GCSFileSystem(FileSystemBase):
        """Wrapper for dask's GCSFileSystem."""
        fs_cls = gcsfs.GCSFileSystem
        scheme = 'gs'
        is_remote = True

        @allow_pathlib
        def remove(self, *args, **kwargs):
            """Remove file."""
            self.fs.rm(*args, **kwargs)

        def makedirs(self, *args, **kwargs):
            raise NotImplementedError


    FILESYSTEMS['gs'] = GCSFileSystem
    FILESYSTEMS['gcs'] = GCSFileSystem
# endregion


# region S3
if s3fs is not None:

    class S3FileSystem(FileSystemBase):
        fs_cls = s3fs.S3FileSystem
        scheme = 's3'
        is_remote = True

        @allow_pathlib
        def touch(self, *args, **kwargs):
            return self.fs.touch(*args, **kwargs)

        def makedirs(self, *args, **kwargs):
            pass

        def rmdir(self, path, **kwargs):
            pass

        def put(self, filename, path, **kwargs):
            from drfs.path import asstr
            filename, path = asstr(filename), asstr(path)
            return self.fs.put(filename, path, **kwargs)

        def get(self, path, filename, **kwargs):
            from drfs.path import asstr
            path, filename = asstr(path), asstr(filename)
            return self.fs.get(path, filename, **kwargs)


    FILESYSTEMS['s3'] = S3FileSystem
# endregion


# region Azure
if abfs is not None:
    class AzureBlobFileSystem(FileSystemBase):
        fs_cls = abfs.DaskAzureBlobFileSystem
        scheme = 'abfs'
        is_remote = True
        
        @allow_pathlib
        def exists(self, path, *args, **kwargs):
            return self.fs.exists(*extract_abfs_parts(path)[1:],
                                  *args, **kwargs)

        @return_pathlib
        @handle_schemes
        @allow_pathlib
        def ls(self, path, *args, **kwargs):
            acc, cont, rest = extract_abfs_parts(path)
            res = self.fs.ls(cont, os.path.join(rest, '*'), *args, **kwargs)
            return [os.path.join(acc, cont, item) for item in res]
    
    def extract_abfs_parts(path):
        import re
        match = re.match('abfs://(.*?)/(.*?)/(.*)', path)
        if match is None:
            raise ValueError(f"Path {path} doesn't match abfs path pattern.")
        account, container, rest = match.groups()
        return account, container, rest
    
    FILESYSTEMS['abfs'] = AzureBlobFileSystem
    
# endregion


def get_fs(path, opts=None, rtype='instance'):
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
    try:
        protocol = path.scheme
    except AttributeError:
        protocol = urllib.parse.urlparse(str(path)).scheme

    try:
        cls = FILESYSTEMS[protocol]
        if rtype == 'class':
            return cls
    except KeyError:
        raise KeyError(f"No filesystem for protocol {protocol}. Try "
                       f"installing it. Available protocols are: "
                       f"{set(FILESYSTEMS.keys())}")
    opts_ = getattr(settings, 'FS_OPTS', {}).copy()  # type: dict
    if opts is not None:
        opts_.update(opts)
    if cls is AzureBlobFileSystem and 'account_name' not in opts_:
        opts_['account_name'] = extract_abfs_parts(path)[0]
    return cls(**opts_)

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
from .util import allow_pathlib, return_pathlib, return_schemes, maybe_remove_scheme

FILESYSTEMS = {}


class FileSystemBase:
    """File System Base

    This is a class that wraps other file system classes to provide consistency API
    across all file system implementations.

    Attributes
    ----------
    fs_cls: Type
        wrapped class, will be managed and instantiated by a subclass of this class.
    scheme: str
        which scheme to use for paths on this storage provider e.g. gcs, s3, file, adl.
    is_remote: bool
        should be set to true if the filesystem is a a remote filesystem.
    supports_scheme: bool
        should be set to true if the underlying filesystem supports uris
        containing a scheme. If set to true this class will strip the scheme as
        specified in the above attribute. E.g. `adl://store/some/file` will be received
        as `/store/some/file
    """

    fs_cls = None  # type: type
    scheme = None  # type: str
    is_remote = None  # type: bool
    supports_scheme = True  # type: bool

    def __init__(self, *args, **kwargs):
        if self.fs_cls is None:
            # Sometimes, like in LocalFileSystem, we don't need underlying fs
            self.fs = None
        else:
            self.fs = self.fs_cls(*args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def open(self, path, *args, **kwargs):
        return self.fs.open(path, *args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def exists(self, path, *args, **kwargs):
        return self.fs.exists(path, *args, **kwargs)

    @return_pathlib
    @return_schemes
    @allow_pathlib
    @maybe_remove_scheme
    def ls(self, path, *args, **kwargs):
        return self.fs.ls(path, *args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def remove(self, path, *args, **kwargs):
        try:
            return self.fs.remove(path, *args, **kwargs)
        except AttributeError:
            return self.fs.rm(path, *args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def copy(self, path, *args, **kwargs):
        try:
            return self.fs.copy(path, *args, **kwargs)
        except AttributeError:
            return self.fs.cp(path, *args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def move(self, path, *args, **kwargs):
        try:
            return self.fs.mv(path, *args, **kwargs)
        except AttributeError:
            return self.fs.move(path, *args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def mv(self, path, *args, **kwargs):
        self.move(path, *args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def makedirs(self, path, *args, **kwargs):
        try:
            return self.fs.makedirs(path, *args, **kwargs)
        except AttributeError:
            return self.fs.mkdir(path, *args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def rmdir(self, path, *args, **kwargs):
        return self.fs.rmdir(path, *args, **kwargs)

    @allow_pathlib
    @maybe_remove_scheme
    def info(self, path, *args, **kwargs):
        return self.fs.info(path, *args, **kwargs)

    @return_pathlib
    @return_schemes
    @allow_pathlib
    @maybe_remove_scheme
    def walk(self, *args, **kwargs):
        return self.fs.walk(*args, **kwargs)

    @return_pathlib
    @return_schemes
    @allow_pathlib
    @maybe_remove_scheme
    def glob(self, *args, **kwargs):
        return self.fs.glob(*args, **kwargs)

    def cp(self, *args, **kwargs):
        """cp is an alias for copy"""
        return self.copy(*args, **kwargs)

    def rm(self, *args, **kwargs):
        """rm is an alias for remove"""
        return self.remove(*args, **kwargs)

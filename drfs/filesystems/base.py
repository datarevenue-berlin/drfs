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
from .util import allow_pathlib, return_pathlib, return_schemes, \
    strip_input_schemes

FILESYSTEMS = {}


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
    @return_schemes
    @allow_pathlib
    @strip_input_schemes
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
    @return_schemes
    @allow_pathlib
    def walk(self, *args, **kwargs):
        return self.fs.walk(*args, **kwargs)

    @return_pathlib
    @return_schemes
    @allow_pathlib
    def glob(self, *args, **kwargs):
        return self.fs.glob(*args, **kwargs)

    def cp(self, *args, **kwargs):
        """cp is an alias for copy"""
        return self.copy(*args, **kwargs)

    def rm(self, *args, **kwargs):
        """rm is an alias for remove"""
        return self.remove(*args, **kwargs)

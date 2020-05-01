from fsspec.implementations import memory as memfs

from drfs.filesystems.base import FILESYSTEMS, FileSystemBase
from drfs.filesystems.util import allow_pathlib


class MemoryFileSystem(FileSystemBase):
    fs_cls = memfs.MemoryFileSystem
    scheme = 'memory'
    is_remote = True
    supports_scheme = False

    @allow_pathlib
    def touch(self, *args, **kwargs):
        return self.fs.touch(*args, **kwargs)

    @allow_pathlib
    def makedirs(self, *args, **kwargs):
        self.fs.makedirs(*args, **kwargs)

    @allow_pathlib
    def rmdir(self, path, **kwargs):
        self.fs.rmdir(path, **kwargs)

    def put(self, filename, path, **kwargs):
        from drfs.path import asstr
        filename, path = asstr(filename), asstr(path)
        return self.fs.put(filename, path, **kwargs)

    def get(self, path, filename, **kwargs):
        from drfs.path import asstr
        path, filename = asstr(path), asstr(filename)
        return self.fs.get(path, filename, **kwargs)


FILESYSTEMS['memory'] = MemoryFileSystem

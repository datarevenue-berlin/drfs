import s3fs

from drfs.filesystems.base import FILESYSTEMS, FileSystemBase
from drfs.filesystems.util import allow_pathlib


class S3FileSystem(FileSystemBase):
    fs_cls = s3fs.S3FileSystem
    scheme = "s3"
    is_remote = True

    @allow_pathlib
    def touch(self, *args, **kwargs):
        return self.fs.touch(*args, **kwargs)

    def makedirs(self, *args, **kwargs):
        pass

    def rmdir(self, path, **kwargs):
        pass

    def rm(self, path, recursive=False, **kwargs):
        return self.fs.rm(path, recursive=recursive, **kwargs)

    def put(self, filename, path, **kwargs):
        from drfs.path import asstr

        filename, path = asstr(filename), asstr(path)
        return self.fs.put(filename, path, **kwargs)

    def get(self, path, filename, **kwargs):
        from drfs.path import asstr

        path, filename = asstr(path), asstr(filename)
        return self.fs.get(path, filename, **kwargs)


FILESYSTEMS["s3"] = S3FileSystem

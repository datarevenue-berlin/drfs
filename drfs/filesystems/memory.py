from fsspec.implementations import memory as memfs

from drfs.filesystems.base import FILESYSTEMS, FileSystemBase
from drfs.filesystems.util import allow_pathlib, maybe_remove_scheme


class MemoryFileSystem(FileSystemBase):
    fs_cls = memfs.MemoryFileSystem
    scheme = "memory"
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

    @allow_pathlib
    @maybe_remove_scheme
    def exists(self, path):
        if self.fs.exists(path):
            return True
        elif path in self.fs.pseudo_dirs:
            return True
        else:
            for k in self.fs.store.keys():
                if k.startswith(path):
                    return True
        return False

    @allow_pathlib
    @maybe_remove_scheme
    def rm(self, path, recursive=False):
        if recursive:
            self._recursive_rm(path)
        else:
            self.fs.rm(path)

    def _recursive_rm(self, path):
        for res in self.fs.ls(path, detail=True):
            if res["type"] == "directory":
                self._recursive_rm(res["name"])
            else:
                self.fs.rm(res["name"])

    def put(self, filename, path, **kwargs):
        from drfs.path import asstr

        filename, path = asstr(filename), asstr(path)
        return self.fs.put(filename, path, **kwargs)

    def get(self, path, filename, **kwargs):
        from drfs.path import asstr

        path, filename = asstr(path), asstr(filename)
        return self.fs.get(path, filename, **kwargs)


FILESYSTEMS["memory"] = MemoryFileSystem

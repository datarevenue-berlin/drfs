import builtins
import datetime
import os
import shutil
from glob import glob as glob_

import pytz

from drfs.filesystems.util import allow_pathlib, return_pathlib
from .base import FILESYSTEMS, FileSystemBase


class LocalFileSystem(FileSystemBase):
    """Emulates a remote filesystem on the local disk."""

    fs_cls = None  # we could do even without subclassing FSBase
    scheme = ""
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
    def remove(self, path, recursive=False):
        """Remove a file or a directory which may be non-empty."""
        try:
            os.remove(path)
        except (IsADirectoryError, PermissionError):
            if not recursive:
                self.rmdir(path)
            else:
                shutil.rmtree(path)

    @return_pathlib
    @allow_pathlib
    def ls(self, path):
        """List directory."""
        if os.path.exists(path):
            return list(map(lambda x: os.path.join(path, x), os.listdir(path)))
        return list()

    @allow_pathlib
    def move(self, src, dst):
        """Move file or directory. Source parent dir will be created."""
        self._makedirs_parent(dst)
        shutil.move(src, dst)

    @allow_pathlib
    def mv(self, src, dst):
        self.move(src, dst)

    @allow_pathlib
    def copy(self, src, dst):
        self._makedirs_parent(dst)
        shutil.copyfile(src, dst)

    @allow_pathlib
    def rmdir(self, path):
        """Remove directory."""
        os.rmdir(path)

    @allow_pathlib
    def info(self, path):
        """Get a dict with only LastModified time in UTC."""
        mtime = os.path.getmtime(path)
        return {"LastModified": datetime.datetime.fromtimestamp(mtime, pytz.UTC)}

    @return_pathlib
    @allow_pathlib
    def walk(self, path):
        """Walk over all files in this directory (recursively)."""
        return [
            os.path.join(root, f) for root, dirs, files in os.walk(path) for f in files
        ]

    @return_pathlib
    @allow_pathlib
    def glob(self, path):
        """Find files by glob-matching."""
        return glob_(path)

    @allow_pathlib
    def touch(self, path):
        self.open(path, "w").close()


FILESYSTEMS[""] = LocalFileSystem
FILESYSTEMS["file"] = LocalFileSystem

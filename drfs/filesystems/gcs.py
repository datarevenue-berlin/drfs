import gcsfs

from drfs.filesystems.base import FILESYSTEMS, FileSystemBase
from drfs.filesystems.util import allow_pathlib


class GCSFileSystem(FileSystemBase):
    """Wrapper for dask's GCSFileSystem."""

    fs_cls = gcsfs.GCSFileSystem
    scheme = "gs"
    is_remote = True

    @allow_pathlib
    def remove(self, *args, **kwargs):
        """Remove file."""
        self.fs.rm(*args, **kwargs)

    def makedirs(self, *args, **kwargs):
        raise NotImplementedError


FILESYSTEMS["gs"] = GCSFileSystem
FILESYSTEMS["gcs"] = GCSFileSystem

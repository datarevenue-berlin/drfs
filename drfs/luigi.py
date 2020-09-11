import os

from drfs.filesystems import get_fs

try:
    from luigi.target import FileSystemTarget
except ImportError:
    raise ImportError("Could not import luigi library. Try installing it.")


class FileTarget(FileSystemTarget):
    def __init__(self, path, **kwargs):
        """Target for any kind of storage. Infers file system automatically.

        Parameters
        ----------
        path: str
            Path to the file.
        **kwargs
            Will be used as filesystem options. (Options from settings are used
            by default, you can overwrite them here.)
        """
        super(FileTarget, self).__init__(str(path))
        self.storage_options = kwargs

    @property
    def fs(self):
        return get_fs(self.path, opts=self.storage_options, rtype="instance")

    def open(self, *args, **kwargs):
        return self.fs.open(self.path, *args, **kwargs)

    def makedirs(self, *args, **kwargs):
        self.fs.makedirs(os.path.dirname(self.path), *args, **kwargs)

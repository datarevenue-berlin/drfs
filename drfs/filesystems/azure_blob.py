import os

import azureblobfs.dask as abfs

from drfs.filesystems.base import FILESYSTEMS, FileSystemBase
from drfs.filesystems.util import allow_pathlib, return_pathlib, return_schemes


class AzureBlobFileSystem(FileSystemBase):
    fs_cls = abfs.DaskAzureBlobFileSystem
    scheme = "abfs"
    is_remote = True

    @allow_pathlib
    def exists(self, path, *args, **kwargs):
        return self.fs.exists(*extract_abfs_parts(path)[1:], *args, **kwargs)

    @return_pathlib
    @return_schemes
    @allow_pathlib
    def ls(self, path, *args, **kwargs):
        acc, cont, rest = extract_abfs_parts(path)
        res = self.fs.ls(cont, os.path.join(rest, "*"), *args, **kwargs)
        return [os.path.join(acc, cont, item) for item in res]


def extract_abfs_parts(path):
    import re

    match = re.match("abfs://(.*?)/(.*?)/(.*)", path)
    if match is None:
        raise ValueError(f"Path {path} doesn't match abfs path pattern.")
    account, container, rest = match.groups()
    return account, container, rest


FILESYSTEMS["abfs"] = AzureBlobFileSystem

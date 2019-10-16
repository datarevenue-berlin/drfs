from dask_adlfs import DaskAdlFileSystem

from drfs.filesystems.base import FILESYSTEMS, FileSystemBase
from drfs.filesystems.util import allow_pathlib, extract_azure_parts


class AzureDataLakeFileSystem(FileSystemBase):
    fs_cls = DaskAdlFileSystem
    scheme = 'adl'
    is_remote = True

    @allow_pathlib
    def exists(self, path, *args, **kwargs):
        return self.fs.exists(*extract_azure_parts(path)[1:],
                              *args, **kwargs)

    # @return_pathlib
    # @return_schemes
    # @allow_pathlib
    # def ls(self, path, *args, **kwargs):
    #     acc, cont, rest = extract_azure_parts(path)
    #     res = self.fs.ls(cont, os.path.join(rest, '*'), *args, **kwargs)
    #     return [os.path.join(acc, cont, item) for item in res]


FILESYSTEMS['adl'] = AzureDataLakeFileSystem

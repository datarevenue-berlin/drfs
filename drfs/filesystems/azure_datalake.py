from azure.datalake.store import lib, AzureDLFileSystem

from drfs.filesystems.base import FileSystemBase, FILESYSTEMS


class AzureDataLakeFileSystem(FileSystemBase):
    fs_cls = AzureDLFileSystem
    scheme = 'adl'
    is_remote = True
    supports_scheme = False

    def __init__(self, tenant_id=None, client_id=None, client_secret=None,
                 **kwargs):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.store_name = kwargs['host']
        self.kwargs = kwargs
        self.kwargs['store_name'] = kwargs['host']
        token = lib.auth(tenant_id=self.tenant_id,
                         client_id=self.client_id,
                         client_secret=self.client_secret)
        self.kwargs['token'] = token
        self.fs = AzureDLFileSystem(**self.kwargs)


FILESYSTEMS[AzureDataLakeFileSystem.scheme] = AzureDataLakeFileSystem

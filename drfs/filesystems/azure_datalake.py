from azure.datalake.store import lib, AzureDLFileSystem
from drfs.filesystems.base import FileSystemBase, FILESYSTEMS


class AzureDataLakeFileSystem(FileSystemBase):
    fs_cls = AzureDLFileSystem
    scheme = "adl"
    is_remote = True
    supports_scheme = False

    def __init__(self, tenant_id=None, client_id=None, client_secret=None, **kwargs):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.kwargs = kwargs
        # self.kwargs['store_name'] = kwargs['host']
        token = lib.auth(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        self.kwargs["token"] = token
        self.fs = AzureDLFileSystem(**self.kwargs)

    def _parse_store_name(self, path):
        from drfs.path import RemotePath

        if not isinstance(path, RemotePath):
            path = RemotePath(path)

        store_name, path = path.hostname, path.path
        if store_name == "":
            raise ValueError(
                "Can't connect without store name. Please provide the path in the "
                "following form: 'adl://STORE_NAME/folder/file.extension'!"
            )
        return store_name, path

    def _connect(self, path):
        self.fs.kwargs["store_name"], path = self._parse_store_name(path)
        self.fs.connect()
        return path

    def _add_store_name(self, p):
        from drfs.path import RemotePath

        parts = p.parts
        part0 = parts[0].split("/")[2]
        drv = parts[0].replace(part0, self.fs.kwargs["store_name"])
        return RemotePath(drv, part0, *parts[1:])

    def ls(self, path, *args, **kwargs):
        path = self._connect(path)
        return [self._add_store_name(p) for p in super().ls(path, *args, **kwargs)]

    def open(self, path, *args, **kwargs):
        path = self._connect(path)
        return super().open(path, *args, **kwargs)

    def exists(self, path, *args, **kwargs):
        path = self._connect(path)
        return super().exists(path, *args, **kwargs)

    def remove(self, path, *args, **kwargs):
        path = self._connect(path)
        return super().remove(path, *args, **kwargs)

    def mv(self, path, *args, **kwargs):
        path = self._connect(path)
        return super().mv(path, *args, **kwargs)

    def makedirs(self, path, *args, **kwargs):
        path = self._connect(path)
        return super().makedirs(path, *args, **kwargs)

    def rmdir(self, path, *args, **kwargs):
        path = self._connect(path)
        return super().rmdir(path, *args, **kwargs)

    def info(self, path, *args, **kwargs):
        path = self._connect(path)
        return super().info(path, *args, **kwargs)

    def walk(self, *args, **kwargs):
        arg0 = self._connect(args[0])
        return [
            self._add_store_name(p) for p in super().walk(arg0, *args[1:], **kwargs)
        ]

    def glob(self, *args, **kwargs):
        arg0 = self._connect(args[0])
        return [
            self._add_store_name(p) for p in super().glob(arg0, *args[1:], **kwargs)
        ]


FILESYSTEMS[AzureDataLakeFileSystem.scheme] = AzureDataLakeFileSystem

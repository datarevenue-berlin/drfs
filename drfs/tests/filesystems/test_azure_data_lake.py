import pytest
from azure.datalake.store import AzureDLFileSystem
from mock import MagicMock

from drfs.filesystems import azure_datalake


@pytest.fixture(autouse=True)
def mock_azure_fs_native(monkeypatch):
    fs = MagicMock(spec=AzureDLFileSystem)
    fs.ls.return_value = [
        'folder/directory/file.txt',
        'folder/directory/file2.txt',
        'folder/directory/file3.txt'
    ]
    fs.glob.return_value = [
        'folder/directory/file.txt',
        'folder/directory/file2.txt',
        'folder/directory/file3.txt'
    ]
    fs.kwargs = {}
    cls = MagicMock()
    cls.return_value = fs
    monkeypatch.setattr(azure_datalake, 'AzureDLFileSystem', cls)
    monkeypatch.setattr(azure_datalake.lib, 'auth', lambda *args, **kwargs: 'token')


def test_custom_connect():
    fs = azure_datalake.AzureDataLakeFileSystem()
    path = fs._connect('adl://intvanprofi/some/path.txt')
    assert fs.fs.kwargs['store_name'] == 'intvanprofi'
    assert not path.startswith('adl://intvanprofi')


def test_ls():
    fs = azure_datalake.AzureDataLakeFileSystem()
    res = fs.ls('adl://intvanprofi/some/path/to/directory')

    fs.fs.ls.assert_called_once_with('/some/path/to/directory')
    for p in res:
        assert p.hostname == 'intvanprofi'
        assert p.scheme == 'adl'


def test_glob():
    fs = azure_datalake.AzureDataLakeFileSystem()
    res = fs.glob('adl://intvanprofi/some/path/to/*.csv')

    fs.fs.glob.assert_called_once_with('/some/path/to/*.csv')

    for p in res:
        assert p.hostname == 'intvanprofi'
        assert p.scheme == 'adl'

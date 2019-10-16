from datetime import datetime
from pathlib import Path

import pytest

from drfs.filesystems.local import LocalFileSystem
from drfs.path import LocalPath


def test_local_filesystem(tmpdir):
    existing_file = tmpdir.join('some_file.txt')
    non_existing_file = tmpdir.join('not_here')
    with open(existing_file, 'w') as f:
        f.write('test')

    fs = LocalFileSystem()
    assert fs.exists(existing_file)
    assert not fs.exists(non_existing_file)
    assert fs.ls(tmpdir) == [existing_file]
    assert 'LastModified' in fs.info(existing_file)
    assert isinstance(fs.info(existing_file)['LastModified'], datetime)
    with pytest.raises(FileNotFoundError):
        fs.info(non_existing_file)
    with fs.open(existing_file, 'r') as f:
        assert f.read() == 'test'
    fs.remove(existing_file)
    assert fs.ls(tmpdir.strpath) == []
    assert not fs.exists(existing_file)


def test_glob_scheme_local(tmpdir):
    fs = LocalFileSystem()
    fs.touch(tmpdir / '/test.txt')
    fs.touch(tmpdir / '/test2.txt')
    fs.touch(tmpdir / 'dir1' / 'deep_test.txt')

    res = fs.glob((tmpdir / '*').strpath)
    assert len(res) == 3  # 2 files + 1 dir
    assert all(isinstance(item, LocalPath) for item in res)
    assert not any('deep_test' in str(item) for item in res)


def test_walk_scheme_local(tmpdir):
    fs = LocalFileSystem()
    fs.touch(tmpdir / '/test.txt')
    fs.touch(tmpdir / '/test2.txt')
    fs.touch(tmpdir / 'dir1' / 'deep_test.txt')

    res = fs.walk(tmpdir.strpath)
    assert len(res) == 3  # 3 files
    assert all(isinstance(item, Path) for item in res)
    assert any('deep_test' in str(item) for item in res)
    assert not any(str(item).rstrip('/').endswith('dir1') for item in res)

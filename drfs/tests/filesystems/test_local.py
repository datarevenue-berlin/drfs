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

    copy_path = tmpdir.join('copy.txt')
    fs.copy(existing_file, copy_path)
    assert copy_path.exists()
    copy_path2 = tmpdir.join('copy2.txt')
    fs.cp(existing_file, copy_path2)
    assert copy_path2.exists()

    fs.remove(existing_file)
    fs.remove(copy_path)
    fs.remove(copy_path2)
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


def test_remove(tmpdir):
    fs = LocalFileSystem()
    empty_dir = tmpdir / 'empty'
    fs.makedirs(empty_dir)
    dir1 = tmpdir / 'dir1'
    file1 = dir1 / 'deep_test.txt'
    fs.touch(file1)

    assert fs.exists(empty_dir)
    fs.remove(empty_dir)
    assert not fs.exists(empty_dir)

    with pytest.raises(OSError):
        fs.remove(dir1)

    assert fs.exists(file1)
    fs.remove(dir1, recursive=True)
    assert not fs.exists(file1)
    assert not fs.exists(dir1)


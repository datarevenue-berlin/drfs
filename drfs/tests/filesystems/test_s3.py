import pytest

from drfs.path import RemotePath

try:
    from drfs.tests.test_filesystem import S3FileSystem
except ImportError:
    pytestmark = pytest.mark.skip(reason="s3fs not installed")


def test_glob_scheme_s3(s3):
    fs = S3FileSystem()
    fs.touch('s3://test-bucket/test2.txt')
    fs.touch('s3://test-bucket/dir1/deep_test.txt')
    res = fs.glob('s3://test-bucket/*')
    assert len(res) == 3  # 2 files + 1 dir
    assert all(isinstance(item, RemotePath) for item in res)
    assert all(str(item).startswith('s3://') for item in res)
    assert not any('deep_test' in str(item) for item in res)

    # # also check walk here to check if it works after hacky stuff in glob
    # res = fs.walk('s3://test-bucket/')
    # assert len(res) == 3  # 3 files
    # assert all(isinstance(item, RemotePath) for item in res)
    # assert all(str(item).startswith('s3://') for item in res)
    # assert any('deep_test' in str(item) for item in res)
    # assert not any(str(item).rstrip('/').endswith('dir1') for item in res)


@pytest.mark.skip("Seems to be buggy. Do we need walk anyway?")
def test_walk_scheme_s3(s3):
    fs = S3FileSystem()
    fs.touch('s3://test-bucket/test2.txt')
    fs.touch('s3://test-bucket/dir1/deep_test.txt')
    res = fs.walk('s3://test-bucket/')
    assert len(res) == 3  # 3 files
    assert all(isinstance(item, RemotePath) for item in res)
    assert all(str(item).startswith('s3://') for item in res)
    assert any('deep_test' in str(item) for item in res)
    assert not any(str(item).rstrip('/').endswith('dir1') for item in res)


def test_remove_recursive(s3):
    fs = S3FileSystem()
    fs.touch("s3://test-bucket/dir1/deep_test.txt")
    fs.touch("s3://test-bucket/dir1/subdir/deeper_test.txt")

    fs.remove("s3://test-bucket/dir1", recursive=True)

    assert not fs.exists("s3://test-bucket/dir1")
    assert not fs.exists("s3://test-bucket/dir1/deep_test.txt")
    assert not fs.exists("s3://test-bucket/dir1/subdir/deeper_test.txt")

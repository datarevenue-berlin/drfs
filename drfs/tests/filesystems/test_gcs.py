import pytest
try:
    from drfs.filesystems.gcs import GCSFileSystem
except ImportError:
    pytestmark = pytest.mark.skip(reason="gcsfs not installed")

# @my_vcr.use_cassette
# def test_gcsfs():
#     fs = GCSFileSystem(TEST_PROJECT, token=GOOGLE_TOKEN)
#     with fs.open('gs://datarevenue-tests/test.txt', 'wb') as f:
#         f.write('hello'.encode())
#     with fs.open('gs://datarevenue-tests/dir1/inner_test.txt', 'wb') as f:
#         f.write('hello'.encode())
#
#     ls_res = fs.ls('gs://datarevenue-tests')
#     assert all(isinstance(item, RemotePath) for item in ls_res)
#     assert any(item.name == 'test.txt' for item in ls_res)
#     assert not any(item.name == 'inner_test.txt' for item in ls_res)
#
#     glob_res = fs.glob('gs://datarevenue-tests/*.txt')
#     assert len(glob_res) == 1
#     assert glob_res == [RemotePath('gs://datarevenue-tests/test.txt')]
#
#     walk_res = fs.walk('gs://datarevenue-tests')
#     assert len(walk_res) == 2
#     assert all(isinstance(item, RemotePath) for item in walk_res)
#     assert any(item.name == 'inner_test.txt' for item in walk_res)
#
#     fs.remove('gs://datarevenue-tests/test.txt')
#     fs.remove('gs://datarevenue-tests/dir1/inner_test.txt')
#     ls2_res = fs.ls('gs://datarevenue-tests')
#     assert len(ls2_res) == 0
#     # Not sure why second call to ls() works because we're using VCR and the
#     # request would is the same, but we expect different result.

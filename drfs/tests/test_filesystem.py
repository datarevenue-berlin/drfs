"""Filesystem tests.

This tests mostly for necessary methods on the filesystems
the functionality itself is not tested but it should be tested
in the corresponding modules that create the (base) classes of
the filesystems.
"""
from pathlib import Path
from warnings import warn

import pytest

from drfs.filesystems import get_fs
from drfs.filesystems.base import FILESYSTEMS
from drfs.filesystems.local import LocalFileSystem
from drfs.filesystems.util import return_pathlib
from drfs.path import RemotePath, aspath

try:
    from drfs.filesystems.s3 import S3FileSystem
except ImportError:
    warn('s3fs not installed, skipping filesystem tests depending on s3fs')
    S3FileSystem = False
try:
    from drfs.filesystems.gcs import GCSFileSystem
    # my_vcr = GCSFSVCR(os.path.join(os.path.dirname(__file__), 'recordings'))\
    #     .my_vcr
except ImportError:
    warn('gcsfs not installed, skipping filesystem tests depending on gcsfs')
    GCSFileSystem = False
try:
    from drfs.filesystems.azure_blob import AzureBlobFileSystem
except ImportError:
    warn('azureblobfs not installed, skipping filesystem tests depending on '
         'it.')
    AzureBlobFileSystem = False


EXPECTED_METHODS = {'remove', 'ls', 'open', 'exists', 'mv', 'makedirs',
                    'rmdir'}


def _get_fs_tuples():
    res = [
        ('user/some_file.txt', LocalFileSystem),
        ('file://user/some_file.txt', LocalFileSystem),
        ('/home/user/some_file.txt', LocalFileSystem),
    ]
    if S3FileSystem:
        res.append(
            ('s3://test-bucket/some_file.txt', S3FileSystem))
    if GCSFileSystem:
        res.extend([
            ('gs://test-bucket/some_file.txt', GCSFileSystem),
            ('gcs://test-bucket/some_file.txt', GCSFileSystem)
        ])
    if AzureBlobFileSystem:
        res.extend([
            ('abfs://test-account/test-container/some_file.txt',
             AzureBlobFileSystem),
        ])
    return res


@pytest.mark.skip('Non-deterministic behaviour of moto. Sometimes this fails. '
                  'Should be investigated and fixed.')
def test_remote_path(s3):
    fs = s3
    assert fs.open('s3://test-bucket/test.txt', 'rb').read()
    p = RemotePath('s3://test-bucket/test.txt')

    with p.open('rb') as fp:
        assert fp.read() == b'bla'

    with p.with_name('test2.txt').open('wb') as fp:
        fp.write(b'bla')

    assert str(next(p.parent.iterdir())) == 's3://test-bucket/test.txt'
    assert p.exists()
    assert p.parent.exists()
    p.unlink()
    assert list(p.parent.iterdir()) == \
        [RemotePath('s3://test-bucket/test2.txt')]
    assert not p.exists()


def test_filesystem_attributes():
    for cls in FILESYSTEMS.values():
        for key in EXPECTED_METHODS:
            assert hasattr(cls, key) and \
                   callable(getattr(cls, key))


@pytest.mark.parametrize('path, fs', _get_fs_tuples())
def test_get_fs(path, fs):
    assert isinstance(get_fs(path), fs)


def relative_path_factory(root):
    def f(arg):
        arg = str(arg)
        return arg.replace(root, '')
    return f


@pytest.mark.usefixtures('s3')
def test_filesystems(tmpdir, s3):
    fs = LocalFileSystem()
    s3 = S3FileSystem()

    bucket = RemotePath('s3://test-bucket')
    tmpdir = Path(str(tmpdir))

    norm_local = relative_path_factory(str(tmpdir))
    # Should it be s3://test-bucket
    norm_s3 = relative_path_factory('s3://test-bucket')

    with tmpdir.joinpath('test.txt').open(mode='w') as fp:
        fp.write('bla')

    assert list(map(norm_local, fs.ls(tmpdir))) == \
           list(map(norm_s3, s3.ls(bucket)))

    assert list(map(norm_local, fs.glob(tmpdir.joinpath('*.txt')))) == \
           list(map(norm_s3, s3.glob(bucket.joinpath('*.txt'))))


@pytest.mark.parametrize("inp, out", [
    ('/home/user', Path('/home/user')),
    (Path('yo'), Path('yo')),
    (['hey', 'ho'], [Path('hey'), Path('ho')]),
    ({'hey', 'ho'}, {Path('hey'), Path('ho')}),
    (('hey', 'ho'), (Path('hey'), Path('ho'))),
    (1, None),
    (['hey', 1], None),
    ('s3://bucket/hey', RemotePath('s3://bucket/hey')),
    ({'s3://hey', 's3://ho'}, {RemotePath('s3://hey'), RemotePath('s3://ho')}),
])
def test_aspath(inp, out):
    if out is not None:
        assert out == aspath(inp)
    else:
        with pytest.raises(TypeError):
            aspath(inp)


def test_return_pathlib():
    class Foo:
        @return_pathlib
        def f(self, s):
            return s

    foo = Foo()
    assert isinstance(foo.f('hey'), Path)
    assert all([isinstance(item, Path) for item in foo.f(['hey', 'ho'])])


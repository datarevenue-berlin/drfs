import pytest

try:
    from drfs.filesystems.azure_blob import extract_abfs_parts
except ImportError:
    pytestmark = pytest.mark.skip(reason="abfs not installed")


def test_extract_abfs_parts():
    assert extract_abfs_parts('abfs://acc/cont/file') \
        == ('acc', 'cont', 'file')
    assert extract_abfs_parts('abfs://acc/cont/dir/file') \
        == ('acc', 'cont', 'dir/file')
    with pytest.raises(ValueError, match="doesn't match abfs"):
        extract_abfs_parts('abfas://acc/cont/dir/file')

import pytest

from drfs import config
from drfs.path import DRPath

def test_is_wildcard():
    assert not DRPath('/home').is_wildcard
    assert DRPath('/home/*').is_wildcard
    assert DRPath('/home/*/yo').is_wildcard
    assert DRPath('/home/**/yo').is_wildcard
    assert DRPath('/home/*.csv').is_wildcard

    assert not DRPath('s3://bucket').is_wildcard
    assert DRPath('s3://bucket/*').is_wildcard
    assert DRPath('s3://bucket/*/yo').is_wildcard
    assert DRPath('s3://bucket/**/yo').is_wildcard
    assert DRPath('s3://bucket/*.csv').is_wildcard


def test_is_template():
    assert not DRPath('/home').is_template
    assert not DRPath('/home/abc{').is_template
    assert not DRPath('/home/abc}{').is_template
    assert DRPath('/home/abc{}').is_template
    assert DRPath('{}/home/abc').is_template
    assert DRPath('/home/abc{yo}').is_template
    assert DRPath('/home/abc{yo/100:.2f}').is_template


def test_remote_div(s3):
    p1 = DRPath('s3://test-bucket/')
    config["fs_opts"] = {"s3": {"access_key": "test"}}
    assert p1.storage_options == config["fs_opts"].get(dict).get("s3", {})
    config["fs_opts"] = {}

    opts = {'key': 'abc', 'secret': 'def'}
    p2 = DRPath('s3://test-bucket', storage_options=opts)
    assert p2.storage_options == opts
    assert p2._acc_real is None
    p2.exists()  # create fs instance with storage options
    assert p2._acc_real is not None
    assert p2._acc_real.fs.key == opts['key']
    assert p2._acc_real.fs.secret == opts['secret']

    p3 = p2 / 'test.txt'
    assert p3.storage_options == p2.storage_options
    assert p3._acc_real is not None
    assert p3._acc_real is p2._acc_real


@pytest.mark.parametrize(
    ("str_path",),
    [
        ("s3://test_bucket",),
        ("/home/test_dir",),
    ]
)
def test_path_get_item(str_path):
    p = DRPath(str_path)

    assert p[:5] == str_path[:5]


@pytest.mark.parametrize(
    ("str_path",),
    [
        ("s3://test_bucket",),
        ("/home/test_dir",),
    ]
)
def test_path_startswith(str_path):
    p = DRPath(str_path)

    assert p.startswith(str_path[:5])

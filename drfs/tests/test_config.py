import pytest

from drfs import config, DRPath
from drfs.filesystems import get_fs


@pytest.fixture()
def s3_opts_config():
    opts = {"key": "test_config"}
    config["fs_opts"]["s3"] = opts
    yield opts
    config["fs_opts"]["s3"] = {}


def test_config_on_path(s3_opts_config):
    p = DRPath("s3://bucket")

    assert p.storage_options == s3_opts_config


def test_config_get_fs(s3_opts_config):
    res = {}

    fs = get_fs("s3://bucket", res)

    assert fs.fs.key == "test_config"


def test_get_fs_no_side_effect():
    expected = config["fs_opts"]["s3"].get(dict).copy()

    get_fs("s3://bucket", opts=dict(config_kwargs={'read_timeout': 600}))

    assert config["fs_opts"]["s3"].get(dict) == expected

from drfs import DRPath
from drfs.settings import FS_OPTS


def test_remote_div(s3):
    p1 = DRPath('s3://test-bucket/')
    assert p1.storage_options == FS_OPTS

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

from drfs.util import strip_scheme


def test_strip_scheme():
    assert strip_scheme('/home') == '/home'
    assert strip_scheme('s3://home') == 'home'
    assert strip_scheme('abfs://home/dir') == 'home/dir'

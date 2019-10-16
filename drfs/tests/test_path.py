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

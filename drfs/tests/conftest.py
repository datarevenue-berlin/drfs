import pytest
from moto import mock_s3


@pytest.fixture()
def s3():
    m = mock_s3()
    m.start()
    import boto3
    import s3fs
    conn = boto3.client('s3')
    conn.create_bucket(Bucket='test-bucket')
    conn.put_object(Bucket='test-bucket', Key='test.txt', Body=b'bla')
    yield s3fs.S3FileSystem(anon=False)
    m.stop()

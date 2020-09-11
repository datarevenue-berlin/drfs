import pytest
from moto import mock_s3


@pytest.fixture()
def s3():
    m = mock_s3()
    m.start()
    import boto3
    import s3fs

    conn = boto3.client("s3")
    conn.create_bucket(Bucket="test-bucket")
    conn.put_object(Bucket="test-bucket", Key="test.txt", Body=b"bla")
    yield s3fs.S3FileSystem(anon=False)
    m.stop()


@pytest.fixture()
def s3_data_dir():
    """Used for testing filesystem and data_import.

    The bucket is purposely named s3-... as this previously introduced a bug and
    it is often the default naming scheme for buckets in the enterprise clouds.
    """
    mock = mock_s3()
    mock.start()
    import boto3
    import s3fs

    conn = boto3.client("s3")
    conn.create_bucket(Bucket="s3-test-bucket")
    fs = s3fs.S3FileSystem()

    for i in range(1, 11):
        fname = f"202002{i:02d}_data.csv"
        with fs.open(f"s3://s3-test-bucket/dump/{fname}", "wb") as fp:
            fp.write(b"hello")

    yield fs
    mock.stop()

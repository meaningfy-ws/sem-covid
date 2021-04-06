
import unittest

from tests.resources.minio_connection import MinioFakeConnection

MINIO_ACCESS_KEY = '2zVld17bTfKk8iu0Eh9H74MywAeDV3WQ'
MINIO_SECRET_KEY = 'ddk9fixfI9qXiMaZu1p2a7BsgY2yDopm'
MINIO_URL = 'srv.meaningfy.ws:9000'
MINIO_TEST_BUCKET = 'test-ml-experiments'

minio = MinioFakeConnection(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_TEST_BUCKET)


class TestTargetGroupsRefactoring(unittest.TestCase):
    pass

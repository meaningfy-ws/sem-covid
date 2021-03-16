#!/usr/bin/python3

# minio_adapter.py
# Date:  02/03/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import io
import logging

from minio import Minio
from minio.deleteobjects import DeleteObject

logger = logging.getLogger('lam-fetcher')


class MinioAdapter:

    def __init__(self, minio_url: str, minio_access_key: str, minio_secret_key: str, minio_bucket: str):
        self.minio_url = minio_url
        self.minio_access_key = minio_access_key
        self.minio_secret_key = minio_secret_key
        self.minio_bucket = minio_bucket

        logger.info('Connecting to Minio instance on ' + self.minio_url)
        self.minio_client = Minio(self.minio_url,
                                  access_key=self.minio_access_key,
                                  secret_key=self.minio_secret_key,
                                  secure=False)
        if self.minio_client.bucket_exists(self.minio_bucket):
            logger.info('The bucket ' + self.minio_bucket + ' already exists.')
        else:
            logger.info('Creating the bucket ' + self.minio_bucket + '')
            self.minio_client.make_bucket(self.minio_bucket)
        logger.info('...done.')

    def empty_bucket(self, object_name_prefix=None):
        logger.info('Clearing the ' + self.minio_bucket + ' bucket...')
        objects = self.minio_client.list_objects(self.minio_bucket, prefix=object_name_prefix)
        objects_to_delete = [DeleteObject(x.object_name) for x in objects]
        for error in self.minio_client.remove_objects(self.minio_bucket, objects_to_delete):
            logger.error(f"Deletion error: {error}")

    def get_object(self, object_name):
        with self.minio_client.get_object(self.minio_bucket, object_name) as response:
            return response.read()

    def put_object(self, object_name, content):
        raw_content = io.BytesIO(content)
        raw_content_size = raw_content.getbuffer().nbytes
        self.minio_client.put_object(self.minio_bucket, object_name, raw_content, raw_content_size)
        return raw_content_size

    def put_object_from_string(self, object_name, content_as_string: str):
        return self.put_object(object_name, bytes(content_as_string, encoding='utf8'))

    def list_objects(self, object_prefix):
        return self.minio_client.list_objects(self.minio_bucket, prefix=object_prefix)

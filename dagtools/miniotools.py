#!/usr/bin/python3

# main.py
# Date:  02/03/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import io
import logging
from json import dumps

from minio import Minio
from minio.deleteobjects import DeleteObject


class MinioAdapter:
    def __init__(self, minio_url, minio_access_key, minio_secret_key, minio_bucket):
        self.logger = logging.getLogger('lam-fetcher')
        self.minio_url = minio_url
        self.minio_access_key = minio_access_key
        self.minio_secret_key = minio_secret_key
        self.minio_bucket = minio_bucket
        self.initialize()

    def initialize(self):
        self.logger.info('Connecting to Minio instance on ' + self.minio_url)

        self.minio_client = Minio(
            self.minio_url,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False
        )
        self.logger.info('...done.')

        if self.minio_client.bucket_exists(self.minio_bucket):
            self.logger.info('Bucket ' + self.minio_bucket + ' already exists.')
        else:
            self.logger.info('Bucket ' + self.minio_bucket + ' does not exist. Creating...')
            self.minio_client.make_bucket(self.minio_bucket)
            self.logger.info('...done.')

    def empty_bucket(self):
        self.logger.info('Clearing the ' + self.minio_bucket + ' bucket...')
        objects = self.minio_client.list_objects(self.minio_bucket)
        objects_to_delete = [DeleteObject(x.object_name) for x in objects]
        for error in self.minio_client.remove_objects(self.minio_bucket, objects_to_delete):
            self.logger.error("Deletion error: {}".format(error))

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

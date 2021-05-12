#!/usr/bin/python3

# minio_object_storage.py
# Date:  02/03/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import io
import logging

from minio import Minio
from minio.deleteobjects import DeleteObject
from sem_covid import config
from sem_covid.adapters.abstract_storage import ObjectStorageABC

logger = logging.getLogger(__name__)


class MinioObjectStorage(ObjectStorageABC):

    def __init__(self, minio_bucket: str,
                 minio_url: str = config.MINIO_URL,
                 minio_access_key: str = config.MINIO_ACCESS_KEY,
                 minio_secret_key: str = config.MINIO_SECRET_KEY):
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

    def clear_storage(self, object_name_prefix=None):
        logger.info('Clearing the ' + self.minio_bucket + ' bucket...')
        objects = self.minio_client.list_objects(self.minio_bucket, prefix=object_name_prefix)
        objects_to_delete = [DeleteObject(x.object_name) for x in objects]
        for error in self.minio_client.remove_objects(self.minio_bucket, objects_to_delete):
            logger.error(f"Deletion error: {error}")

    def get_object(self, object_name: str):
        with self.minio_client.get_object(self.minio_bucket, object_name) as response:
            return response.read()

    def put_object(self, object_name: str, content) -> int:
        if type(content) == str:
            raw_content = bytes(content, encoding='utf8')
        else:
            raw_content = io.BytesIO(content)
        raw_content_size = raw_content.getbuffer().nbytes
        self.minio_client.put_object(self.minio_bucket, object_name, raw_content, raw_content_size)
        return raw_content_size

    def list_objects(self, object_prefix: str):
        return self.minio_client.list_objects(self.minio_bucket, prefix=object_prefix)

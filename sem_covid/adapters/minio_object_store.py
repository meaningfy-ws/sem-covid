#!/usr/bin/python3

# minio_object_store.py
# Date:  02/03/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import io
import logging

from minio import Minio
from minio.deleteobjects import DeleteObject

from sem_covid.adapters.abstract_store import ObjectStoreABC

logger = logging.getLogger(__name__)


# TODO : Add documentation for this implementation
class MinioObjectStore(ObjectStoreABC):

    def __init__(self, minio_bucket: str, minio_client: Minio):
        self.minio_bucket = minio_bucket

        logger.info('Connecting to Minio instance')
        self.minio_client = minio_client
        if self.minio_client.bucket_exists(self.minio_bucket):
            logger.info('The bucket ' + self.minio_bucket + ' already exists.')
        else:
            logger.info('Creating the bucket ' + self.minio_bucket + '')
            self.minio_client.make_bucket(self.minio_bucket)
        logger.info('...done.')

    def empty_bucket(self, object_name_prefix: str = None):
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
            raw_content = io.BytesIO(bytes(content, encoding='utf8'))
        else:
            raw_content = io.BytesIO(content)
        raw_content_size = raw_content.getbuffer().nbytes
        self.minio_client.put_object(self.minio_bucket, object_name, raw_content, raw_content_size)
        return raw_content_size

    def list_objects(self, object_name_prefix: str):
        return self.minio_client.list_objects(self.minio_bucket, prefix=object_name_prefix)

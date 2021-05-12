from sem_covid import config
from sem_covid.adapters.es_feature_storage import ESFeatureStorage
from sem_covid.adapters.es_index_storage import ESIndexStorage
from sem_covid.adapters.minio_object_storage import MinioObjectStorage


class StorageRegistry:

    @staticmethod
    def es_index_storage():
        return ESIndexStorage(config.ELASTICSEARCH_HOST_NAME,
                              config.ELASTICSEARCH_PORT,
                              config.ELASTICSEARCH_USERNAME,
                              config.ELASTICSEARCH_PASSWORD)

    @staticmethod
    def minio_object_storage(minio_bucket: str):
        return MinioObjectStorage(minio_bucket,
                                  config.MINIO_URL,
                                  config.MINIO_ACCESS_KEY,
                                  config.MINIO_SECRET_KEY
                                  )

    @staticmethod
    def es_feature_storage():
        return ESFeatureStorage(StorageRegistry.es_index_storage())


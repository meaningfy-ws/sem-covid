from sem_covid import config
from sem_covid.adapters.es_feature_store import ESFeatureStore
from sem_covid.adapters.es_index_store import ESIndexStore
from sem_covid.adapters.minio_object_store import MinioObjectStore


class StoreRegistry:

    @staticmethod
    def es_index_store():
        return ESIndexStore(config.ELASTICSEARCH_HOST_NAME,
                            config.ELASTICSEARCH_PORT,
                            config.ELASTICSEARCH_USERNAME,
                            config.ELASTICSEARCH_PASSWORD)

    @staticmethod
    def minio_object_store(minio_bucket: str):
        return MinioObjectStore(minio_bucket,
                                config.MINIO_URL,
                                config.MINIO_ACCESS_KEY,
                                config.MINIO_SECRET_KEY
                                )

    @staticmethod
    def es_feature_store():
        return ESFeatureStore(StoreRegistry.es_index_store())


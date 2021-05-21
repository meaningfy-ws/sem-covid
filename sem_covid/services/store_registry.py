from es_pandas import es_pandas
from minio import Minio

from sem_covid import config
from sem_covid.adapters.es_feature_store import ESFeatureStore
from sem_covid.adapters.es_index_store import ESIndexStore
from sem_covid.adapters.minio_object_store import MinioObjectStore


class StoreRegistry:

    @staticmethod
    def es_index_store():
        es_pandas_client = es_pandas(config.ELASTICSEARCH_HOST_NAME,
                                     http_auth=(config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD),
                                     port=config.ELASTICSEARCH_PORT, http_compress=True)
        return ESIndexStore(es_pandas_client)

    @staticmethod
    def minio_object_store(minio_bucket: str):
        minio_client = Minio(config.MINIO_URL,
                             access_key=config.MINIO_ACCESS_KEY,
                             secret_key=config.MINIO_SECRET_KEY,
                             secure=False)
        return MinioObjectStore(minio_bucket, minio_client)

    @staticmethod
    def es_feature_store():
        return ESFeatureStore(StoreRegistry.es_index_store())

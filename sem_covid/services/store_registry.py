import abc
from abc import abstractmethod
from es_pandas import es_pandas
from minio import Minio

from sem_covid import config
from sem_covid.adapters.abstract_store import IndexStoreABC, FeatureStoreABC, ObjectStoreABC, TripleStoreABC
from sem_covid.adapters.es_feature_store import ESFeatureStore
from sem_covid.adapters.es_index_store import ESIndexStore
from sem_covid.adapters.minio_object_store import MinioObjectStore
from sem_covid.adapters.sparql_triple_store import SPARQLTripleStore


class StoreRegistryManagerABC(abc.ABC):

    @abstractmethod
    def es_index_store(self) -> IndexStoreABC:
        pass

    @abstractmethod
    def minio_object_store(self, minio_bucket: str) -> ObjectStoreABC:
        pass

    @abstractmethod
    def es_feature_store(self) -> FeatureStoreABC:
        pass

    @abstractmethod
    def sparql_triple_store(self, endpoint_url: str) -> TripleStoreABC:
        pass


class StoreRegistryManager(StoreRegistryManagerABC):

    def sparql_triple_store(self, endpoint_url: str) -> TripleStoreABC:
        return SPARQLTripleStore(endpoint_url=endpoint_url)

    def es_index_store(self) -> IndexStoreABC:
        es_pandas_client = es_pandas(config.ELASTICSEARCH_HOST_NAME,
                                     http_auth=(config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD),
                                     port=config.ELASTICSEARCH_PORT, http_compress=True)
        return ESIndexStore(es_pandas_client)

    def minio_object_store(self, minio_bucket: str) -> ObjectStoreABC:
        minio_client = Minio(config.MINIO_URL,
                             access_key=config.MINIO_ACCESS_KEY,
                             secret_key=config.MINIO_SECRET_KEY,
                             secure=False)
        return MinioObjectStore(minio_bucket, minio_client)

    def es_feature_store(self) -> FeatureStoreABC:
        return ESFeatureStore(StoreRegistry.es_index_store())


StoreRegistry = StoreRegistryManager()

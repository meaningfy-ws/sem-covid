#!/usr/bin/python3

# store_registry.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to achieve a simple method of access to different types of stores.
    Simplified access is achieved through a preconfigured stores register.
"""

from abc import ABC, abstractmethod

from es_pandas import es_pandas
from minio import Minio

from sem_covid import config
from sem_covid.adapters.abstract_store import IndexStoreABC, FeatureStoreABC, ObjectStoreABC, TripleStoreABC
from sem_covid.adapters.es_feature_store import ESFeatureStore
from sem_covid.adapters.es_index_store import ESIndexStore
from sem_covid.adapters.minio_feature_store import MinioFeatureStore
from sem_covid.adapters.minio_object_store import MinioObjectStore
from sem_covid.adapters.sparql_triple_store import SPARQLTripleStore

MINIO_FEATURE_BUCKET = 'fs-bucket'


class StoreRegistryABC(ABC):

    @abstractmethod
    def es_index_store(self) -> IndexStoreABC:
        raise NotImplementedError

    @abstractmethod
    def minio_object_store(self, minio_bucket: str) -> ObjectStoreABC:
        raise NotImplementedError

    @abstractmethod
    def es_feature_store(self) -> FeatureStoreABC:
        raise NotImplementedError

    @abstractmethod
    def minio_feature_store(self) -> FeatureStoreABC:
        raise NotImplementedError

    @abstractmethod
    def sparql_triple_store(self, endpoint_url: str) -> TripleStoreABC:
        raise NotImplementedError


class StoreRegistry(StoreRegistryABC):
    """
        This class performs the register of preconfigured stores.
    """

    def minio_feature_store(self, minio_bucket: str = MINIO_FEATURE_BUCKET) -> FeatureStoreABC:
        """
             This method returns a preconfigured MinioFeatureStore.
         :return:
         """
        return MinioFeatureStore(object_store=self.minio_object_store(minio_bucket))

    def sparql_triple_store(self, endpoint_url: str) -> TripleStoreABC:
        return SPARQLTripleStore(endpoint_url=endpoint_url)

    def es_index_store(self) -> IndexStoreABC:
        """
            This method returns a preconfigured ESIndexStore.
        :return:
        """
        es_pandas_client = es_pandas(config.ELASTICSEARCH_HOST_NAME,
                                     http_auth=(config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD),
                                     port=config.ELASTICSEARCH_PORT, http_compress=True,
                                     timeout=config.ELASTICSEARCH_TIMEOUT)
        return ESIndexStore(es_pandas_client)

    def minio_object_store(self, minio_bucket: str) -> ObjectStoreABC:
        """
            This method returns a preconfigured MinioObjectStore.
        :param minio_bucket: the name of the desired bucket.
        :return:
        """
        minio_client = Minio(config.MINIO_URL,
                             access_key=config.MINIO_ACCESS_KEY,
                             secret_key=config.MINIO_SECRET_KEY,
                             secure=False)
        return MinioObjectStore(minio_bucket, minio_client)

    def es_feature_store(self) -> FeatureStoreABC:
        """
            This method returns a preconfigured ESFeatureStore.
        :return:
        """
        return ESFeatureStore(self.es_index_store())


store_registry = StoreRegistry()

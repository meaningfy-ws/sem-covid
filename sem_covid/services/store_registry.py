#!/usr/bin/python3

# store_registry.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to achieve a simple method of access to different types of stores.
    Simplified access is achieved through a preconfigured stores register.
"""

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
        pass

    def minio_object_store(self, minio_bucket: str) -> ObjectStoreABC:
        pass

    def es_feature_store(self) -> FeatureStoreABC:
        pass

      
class StoreRegistry:
    """
        This class performs the register of preconfigured stores.
    """
    @staticmethod
    def es_index_store() -> IndexStoreABC:
        """
            This method returns a preconfigured ESIndexStore.
        :return:
        """
        es_pandas_client = es_pandas(config.ELASTICSEARCH_HOST_NAME,
                                     http_auth=(config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD),
                                     port=config.ELASTICSEARCH_PORT, http_compress=True)
        return ESIndexStore(es_pandas_client)

    @staticmethod
    def minio_object_store(minio_bucket: str) ->ObjectStoreABC:
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

    @staticmethod
    def es_feature_store() -> FeatureStoreABC:
        """
            This method returns a preconfigured ESFeatureStore.
        :return:
        """
        return ESFeatureStore(StoreRegistry.es_index_store())


StoreRegistry = StoreRegistryManager()

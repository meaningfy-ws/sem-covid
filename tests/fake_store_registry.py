import pathlib

from sem_covid.adapters.abstract_store import IndexStoreABC, ObjectStoreABC, FeatureStoreABC, TripleStoreABC
from sem_covid.services.store_registry import StoreRegistryABC
from tests.fake_storage import FakeIndexStore, FakeObjectStore, FakeFeatureStore, FakeTripleStore
from sem_covid import config
import pandas as pd
from tests import TEST_DATA_PATH

class FakeStoreRegistry(StoreRegistryABC):

    def __init__(self):
        self.fake_index_store = None
        self.fake_minio_object_store = None
        self.fake_es_feature_store = None
        self.fake_sparql_triple_store = None

    def es_index_store(self) -> IndexStoreABC:
        if self.fake_index_store is None:
            self.fake_index_store = FakeIndexStore()

        return self.fake_index_store

    def minio_object_store(self, minio_bucket: str) -> ObjectStoreABC:
        if self.fake_minio_object_store is None:
            self.fake_minio_object_store = FakeObjectStore()

        return self.fake_minio_object_store

    def es_feature_store(self) -> FeatureStoreABC:
        if self.fake_es_feature_store is None:
            self.fake_es_feature_store = FakeFeatureStore()

        return self.fake_es_feature_store

    def minio_feature_store(self) -> FeatureStoreABC:
        if self.fake_es_feature_store is None:
            self.fake_es_feature_store = FakeFeatureStore()

        return self.fake_es_feature_store

    def sparql_triple_store(self, endpoint_url: str) -> TripleStoreABC:
        if self.fake_sparql_triple_store is None:
            self.fake_sparql_triple_store = FakeTripleStore()

        return self.fake_sparql_triple_store


class FakeStoreWithDatasetsRegistry(FakeStoreRegistry):

    def es_index_store(self) -> IndexStoreABC:
        if self.fake_index_store is None:
            self.fake_index_store = FakeIndexStore()
            index_names = [config.PWDB_ELASTIC_SEARCH_INDEX_NAME,
                           config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                           config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                           config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME
                           ]
            for index_name in index_names:
                df = pd.read_json(TEST_DATA_PATH / 'datasets_sample' / f'{index_name}.json')
                self.fake_index_store.put_dataframe(index_name=index_name, content=df)

        return self.fake_index_store

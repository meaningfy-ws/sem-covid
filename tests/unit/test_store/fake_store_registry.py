
from sem_covid.adapters.abstract_store import IndexStoreABC, ObjectStoreABC, FeatureStoreABC, TripleStoreABC
from sem_covid.services.store_registry import StoreRegistryManagerABC
from tests.unit.test_store.fake_storage import FakeIndexStore, FakeObjectStore, FakeFeatureStore, FakeTripleStore


class FakeStoreRegistryManager(StoreRegistryManagerABC):

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

    def sparql_triple_store(self, endpoint_url: str) -> TripleStoreABC:
        if self.fake_sparql_triple_store is None:
            self.fake_sparql_triple_store = FakeTripleStore()

        return self.fake_sparql_triple_store

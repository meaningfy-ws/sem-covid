from sem_covid.adapters.es_feature_store import ESFeatureStore
from sem_covid.adapters.es_index_store import ESIndexStore
from sem_covid.adapters.minio_object_store import MinioObjectStore
from sem_covid.services.store_registry import StoreRegistry


def test_store_registry():
    assert type(StoreRegistry.es_index_store()) == ESIndexStore
    assert type(StoreRegistry.minio_object_store("ds-ireland-timeline")) == MinioObjectStore
    assert type(StoreRegistry.es_feature_store()) == ESFeatureStore

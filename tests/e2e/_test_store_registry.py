from sem_covid.adapters.es_feature_store import ESFeatureStore
from sem_covid.adapters.es_index_store import ESIndexStore
from sem_covid.adapters.minio_object_store import MinioObjectStore
from sem_covid.services.store_registry import store_registry


def test_store_registry():
    assert type(store_registry.es_index_store()) == ESIndexStore
    assert type(store_registry.minio_object_store("ds-ireland-timeline")) == MinioObjectStore
    assert type(store_registry.es_feature_store()) == ESFeatureStore

import pathlib
from sem_covid.services.data_registry import Dataset
from sem_covid.services.store_registry import StoreRegistry


def test_eu_action_timeline_dump():
    minio = StoreRegistry.minio_object_store("tmp-elasticsearch-dump")
    local_path = pathlib.Path(__file__).resolve().parents[1] / 'elasticsearch_dump'
    Dataset().EU_ACTION_TIMELINE.dump_local(local_path)
    Dataset().EU_ACTION_TIMELINE.dump_remote(minio)


def test_pwdb_dump():
    minio = StoreRegistry.minio_object_store("tmp-elasticsearch-dump")
    local_path = pathlib.Path(__file__).resolve().parents[1] / 'elasticsearch_dump'
    Dataset().PWDB.dump_local(local_path)
    Dataset().PWDB.dump_remote(minio)


def test_eu_cellar_dump():
    minio = StoreRegistry.minio_object_store("tmp-elasticsearch-dump")
    local_path = pathlib.Path(__file__).resolve().parents[1] / 'elasticsearch_dump'
    Dataset().EU_CELLAR.dump_local(local_path)
    Dataset().EU_CELLAR.dump_remote(minio)


def test_ireland_action_timeline_dump():
    minio = StoreRegistry.minio_object_store("tmp-elasticsearch-dump")
    local_path = pathlib.Path(__file__).resolve().parents[1] / 'elasticsearch_dump'
    Dataset().IRELAND_ACTION_TIMELINE.dump_local(local_path)
    Dataset().IRELAND_ACTION_TIMELINE.dump_remote(minio)

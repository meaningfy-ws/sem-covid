import pathlib

from sem_covid.adapters.data_source import IndexTabularDataSource
from sem_covid.services.data_registry import Dataset
from sem_covid.services.store_registry import StoreRegistry


def dump_dataset(dataset: IndexTabularDataSource):
    minio = StoreRegistry.minio_object_store("tmp-elasticsearch-dump")
    local_path = pathlib.Path(__file__).resolve().parents[1] / 'elasticsearch_dump'
    dataset.dump_local(local_path)
    dataset.dump_remote(minio)


def test_eu_action_timeline_dump():
    dump_dataset(Dataset().EU_ACTION_TIMELINE)


def test_pwdb_dump():
    dump_dataset(Dataset().PWDB)


def test_eu_cellar_dump():
    dump_dataset(Dataset().EU_CELLAR)


def test_ireland_action_timeline_dump():
    dump_dataset(Dataset().IRELAND_ACTION_TIMELINE)


def test_eu_cellar_enriched_dump():
    dump_dataset(Dataset().EU_CELLAR_ENRICHED)


def test_eu_timeline_enriched_dump():
    dump_dataset(Dataset().EU_ACTION_TIMELINE_ENRICHED)


def test_ireland_timeline_enriched_dump():
    dump_dataset(Dataset().IRELAND_ACTION_TIMELINE_ENRICHED)

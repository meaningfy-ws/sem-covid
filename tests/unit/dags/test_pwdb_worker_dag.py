#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
import hashlib
import json

import pytest

from tests.unit.dags.conftest import AttrDict, fragment_pwdb
from tests.unit.test_store.fake_store_registry import FakeStoreRegistry
from sem_covid.entrypoints.etl_dags.pwdb_worker import DAG_NAME, download_single_source, PWDBDagWorker

store_registry = FakeStoreRegistry()
MINIO_BUCKET_NAME = 'fake_bucket'
APACHE_TIKA_URL = 'www.fake.com'
ES_HOST_NAME = 'fake_host_name'
ES_PORT = '8907'
ES_INDEX_NAME = 'fake_index'
TIKA_FILE_PREFIX = 'tika/'
RESOURCE_FILE_PREFIX = 'res/'


def test_download_single_source():
    source = {'url': 'example.com',
              'failure_reason': 'because'}
    fake_bucket_name = 'fake-bucket-name'
    fake_store_registry = FakeStoreRegistry()
    minio_client = fake_store_registry.minio_object_store(fake_bucket_name)
    load = download_single_source(source, minio_client)
    print(load)

    assert dict == type(load)
    assert load['url'] == 'example.com'
    assert load['failure_reason'] == 'because'
    assert load['content_path'].startswith('res/') == True


def test_pwdb_worker_dag():
    json_file_name = TIKA_FILE_PREFIX + hashlib.sha256(
        "Hardship case fund: Safety net for self-employed".encode('utf-8')).hexdigest() + ".json"
    minio_client = store_registry.minio_object_store('fake_bucket')

    minio_client.put_object(json_file_name, json.dumps(fragment_pwdb()).encode('utf-8'))
    context = {'dag_run': AttrDict({
        "conf": {'filename': json_file_name}})}

    worker_dag = PWDBDagWorker(
        store_registry=store_registry,
        bucket_name=MINIO_BUCKET_NAME,
        apache_tika_url=APACHE_TIKA_URL,
        elasticsearch_index_name=ES_INDEX_NAME,
        elasticsearch_host_name=ES_HOST_NAME,
        elasticsearch_port=ES_PORT
    )
    print(minio_client.list_objects(object_name_prefix=TIKA_FILE_PREFIX))

    worker_dag.extract(**context)
    assert len(minio_client.list_objects(object_name_prefix=TIKA_FILE_PREFIX)) > 0

    with pytest.raises(KeyError):
        worker_dag.extract()

    worker_dag.transform_content(**context)
    assert "content" in minio_client.get_object(
        'tika/4c4917157d621114c4d108fb230ad337650d7c07a786ef914bae62c4c9e8ccd7.json')

    worker_dag.transform_structure()

    tika_filename = TIKA_FILE_PREFIX + hashlib.sha256(
        (str(fragment_pwdb()['identifier'] + fragment_pwdb()['title'])).encode('utf-8')).hexdigest()
    minio_client.put_object(tika_filename, json.dumps(fragment_pwdb()).encode('utf-8'))

    worker_dag.load(**context)


def test_pwdb_worker_has_three_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'Enrich', 'Tika', 'ElasticSearch'}.issubset(set(task_ids))

    enrich_task = dag.get_task('Enrich')
    upstream_task_id = list(map(lambda task: task.task_id, enrich_task.upstream_list))
    assert not upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, enrich_task.downstream_list))
    assert 'Tika' in downstream_task_id

    tika_task = dag.get_task('Tika')
    upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
    assert 'Enrich' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
    assert 'ElasticSearch' in downstream_task_id

    elastic_search_task = dag.get_task('ElasticSearch')
    upstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.upstream_list))
    assert 'Tika' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.downstream_list))
    assert not downstream_task_id

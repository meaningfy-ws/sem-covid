#!/usr/bin/python3

# Date:  03/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

import pytest
from airflow.exceptions import DagNotFound

from tests.unit.test_store.fake_store_registry import FakeStoreRegistry
from sem_covid.entrypoints.etl_dags.pwdb_dags import DAG_NAME, PWDBMasterDag

store_registry = FakeStoreRegistry()
FAKE_MINIO_URL = 'www.fake-url.com'
FAKE_BUCKET_NAME = 'fake_bucket'
FAKE_DATASET_URL = 'http://static.eurofound.europa.eu/covid19db/data/covid19db.json'
FAKE_LOCAL_FILE = 'fake.json'


def test_pwdb_master_dag():
    master_dag = PWDBMasterDag(
        store_registry=store_registry,
        minio_url=FAKE_MINIO_URL,
        bucket_name=FAKE_BUCKET_NAME,
        dataset_url=FAKE_DATASET_URL,
        dataset_local_filename=FAKE_LOCAL_FILE
    )
    master_dag.get_steps()
    master_dag.select_assets()

    with pytest.raises(DagNotFound):
        # we test that the work is found and loaded but we don't test triggering in the airflow environment
        master_dag.trigger_workers()


def test_pwdb_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'download_and_split', 'execute_worker_dags'}.issubset(set(task_ids))

    download_and_split_task = dag.get_task('download_and_split')
    upstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.upstream_list))
    assert not upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.downstream_list))
    assert 'execute_worker_dags' in downstream_task_ids

    execute_worker_dags_task = dag.get_task('execute_worker_dags')
    upstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.upstream_list))
    assert 'download_and_split' in upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.downstream_list))
    assert not downstream_task_ids

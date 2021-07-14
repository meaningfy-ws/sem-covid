#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
import logging

from sem_covid.entrypoints.etl_dags.ds_cellar_covid_dags import MASTER_DAG_NAME, WORKER_DAG_NAME

logger = logging.getLogger(__name__)


def test_ds_cellar_covid_master_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=MASTER_DAG_NAME)
    print(f"dags in dag bag: {airflow_dag_bag.dag_ids}")
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


def test_ds_cellar_covid_work_has_three_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=WORKER_DAG_NAME)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'extract_content_with_tika', 'content_cleanup', 'download_documents_and_enrich_json',
            'upload_to_elastic'}.issubset(set(task_ids))
    # {'extract_content_with_tika', 'content_cleanup', 'download_documents_and_enrich_json', 'upload_to_elastic'}
    # {'Enrich', 'Tika', 'Content_cleanup', 'Elasticsearch'}
    # print(set(task_ids))

    enrich_task = dag.get_task('extract_content_with_tika')  # extract_content_with_tika Enrich
    upstream_task_id = list(map(lambda task: task.task_id, enrich_task.upstream_list))
    assert 'download_documents_and_enrich_json' in upstream_task_id  # was not
    downstream_task_id = list(map(lambda task: task.task_id, enrich_task.downstream_list))
    assert 'content_cleanup' in downstream_task_id  # content_cleanup Tika

    tika_task = dag.get_task('content_cleanup')  # content_cleanup Tika
    upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
    assert 'extract_content_with_tika' in upstream_task_id  # extract_content_with_tika Enrich
    downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
    assert 'upload_to_elastic' in downstream_task_id  # upload_to_elastic Content_cleanup

    tika_task = dag.get_task('download_documents_and_enrich_json')  # download_documents_and_enrich_json Content_cleanup
    upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
    assert not upstream_task_id  # not -  Tika
    downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
    assert 'extract_content_with_tika' in downstream_task_id  # extract_content_with_tika Elasticsearch

    elastic_search_task = dag.get_task('upload_to_elastic')  # upload_to_elastic Elasticsearch
    upstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.upstream_list))
    assert 'content_cleanup' in upstream_task_id  # content_cleanup Content_cleanup
    downstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.downstream_list))
    assert not downstream_task_id

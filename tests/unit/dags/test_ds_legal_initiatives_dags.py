#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com


from sem_covid.entrypoints.etl_dags.ds_legal_initiatives_dags import MASTER_DAG_NAME, WORKER_DAG_NAME


def test_ds_legal_initiatives_master_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=MASTER_DAG_NAME)
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


def test_ds_legal_initiatives_worker_has_three_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=WORKER_DAG_NAME)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'Enrich', 'Tika', 'Elasticsearch'}.issubset(set(task_ids))

    enrich_task = dag.get_task('Enrich')
    upstream_task_id = list(map(lambda task: task.task_id, enrich_task.upstream_list))
    assert not upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, enrich_task.downstream_list))
    assert 'Tika' in downstream_task_id

    tika_task = dag.get_task('Tika')
    upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
    assert 'Enrich' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
    assert 'Elasticsearch' in downstream_task_id

    elastic_search_task = dag.get_task('Elasticsearch')
    upstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.upstream_list))
    assert 'Tika' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.downstream_list))
    assert not downstream_task_id

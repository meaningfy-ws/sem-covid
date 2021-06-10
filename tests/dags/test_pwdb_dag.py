#!/usr/bin/python3

# Date:  03/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com


from sem_covid.entrypoints.etl_dags.pwdb import DAG_NAME


def test_pwdb_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    # assert airflow_dag_bag.import_errors == {}
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

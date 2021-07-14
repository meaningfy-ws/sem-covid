#!/usr/bin/python3

# Date:  11/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

import logging

from sem_covid.entrypoints.etl_dags.dummy_debug_dag import MASTER_DAG_NAME, SLAVE_DAG_NAME, DAG_NAME, MASTER_DAG_NAME_2

logger = logging.getLogger(__name__)


def test_dummy_debug_dag_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=MASTER_DAG_NAME)
    logger.info(f"dags in gad bag: {airflow_dag_bag.dag_ids}")
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'prepare_terrain_for_workers', 'wakeup_workers'}.issubset(set(task_ids))

    download_and_split_task = dag.get_task('prepare_terrain_for_workers')
    upstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.upstream_list))
    assert not upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.downstream_list))
    assert 'wakeup_workers' in downstream_task_ids

    execute_worker_dags_task = dag.get_task('wakeup_workers')
    upstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.upstream_list))
    assert 'prepare_terrain_for_workers' in upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.downstream_list))
    assert not downstream_task_ids

    dag = airflow_dag_bag.get_dag(dag_id=SLAVE_DAG_NAME)
    assert dag is not None

    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert dag is not None

    dag = airflow_dag_bag.get_dag(dag_id=MASTER_DAG_NAME_2)
    assert dag is not None

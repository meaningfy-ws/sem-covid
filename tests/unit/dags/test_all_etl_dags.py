#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
import logging

from sem_covid.entrypoints.etl_dags.ds_cellar_covid_dags import MASTER_DAG_NAME as DS_CELLAR_MASTER, \
    WORKER_DAG_NAME as DS_CELLAR_WORKER
from sem_covid.entrypoints.etl_dags.ds_fin_reg_dags import MASTER_DAG_NAME as DS_FIN_REG_MASTER, \
    WORKER_DAG_NAME as DS_FIN_REG_WORKER

from sem_covid.entrypoints.etl_dags.ds_legal_initiatives_dags import MASTER_DAG_NAME as DS_LEG_INIT_MASTER, \
    WORKER_DAG_NAME as DS_LEG_INIT_WORKER
from sem_covid.entrypoints.etl_dags.ds_treaties_dags import MASTER_DAG_NAME as DS_TREATIES_MASTER, \
    WORKER_DAG_NAME as DS_TREATIES_WORKER

logger = logging.getLogger(__name__)


def test_etl_cellar_masters(airflow_dag_bag):
    """
        To test any etl_cellar_dags simply add teh dag name to the list of dag_names below
    """
    dag_names = [DS_CELLAR_MASTER, DS_TREATIES_MASTER, DS_FIN_REG_MASTER, DS_LEG_INIT_MASTER]
    target_dags = [airflow_dag_bag.get_dag(dag_id=dag_id) for dag_id in dag_names]

    for dag in target_dags:
        assert dag is not None
        tasks = dag.tasks
        task_ids = list(map(lambda task: task.task_id, tasks))
        assert {'select_assets', 'trigger_workers'}.issubset(set(task_ids))

        download_and_split_task = dag.get_task('select_assets')
        upstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.upstream_list))
        assert not upstream_task_ids
        downstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.downstream_list))
        assert 'trigger_workers' in downstream_task_ids

        execute_worker_dags_task = dag.get_task('trigger_workers')
        upstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.upstream_list))
        assert 'select_assets' in upstream_task_ids
        downstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.downstream_list))
        assert not downstream_task_ids


def test_etl_cellar_workers(airflow_dag_bag):
    dag_names = [DS_CELLAR_WORKER, DS_TREATIES_WORKER, DS_FIN_REG_WORKER, DS_LEG_INIT_WORKER]
    target_dags = [airflow_dag_bag.get_dag(dag_id=dag_id) for dag_id in dag_names]

    for dag in target_dags:
        logger.info(f"Checking {dag.dag_id}")
        assert dag is not None
        tasks = dag.tasks
        task_ids = list(map(lambda task: task.task_id, tasks))
        assert {'extract', 'transform_structure', 'transform_content',
                'load'}.issubset(set(task_ids))

        enrich_task = dag.get_task('extract')
        upstream_task_id = list(map(lambda task: task.task_id, enrich_task.upstream_list))
        assert not upstream_task_id
        downstream_task_id = list(map(lambda task: task.task_id, enrich_task.downstream_list))
        assert 'transform_structure' in downstream_task_id

        tika_task = dag.get_task('transform_structure')
        upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
        assert 'extract' in upstream_task_id
        downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
        assert 'transform_content' in downstream_task_id

        content_cleanup = dag.get_task('transform_content')
        upstream_task_id = list(map(lambda task: task.task_id, content_cleanup.upstream_list))
        assert 'transform_structure' in upstream_task_id
        downstream_task_id = list(map(lambda task: task.task_id, content_cleanup.downstream_list))
        assert 'load' in downstream_task_id

        elastic_search_task = dag.get_task('load')
        upstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.upstream_list))
        assert 'transform_content' in upstream_task_id
        downstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.downstream_list))
        assert not downstream_task_id

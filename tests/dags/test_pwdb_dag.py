#!/usr/bin/python3

# main.py
# Date:  27/05/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

import logging
import unittest

from airflow.models import DagBag

from sem_covid.entrypoints.etl_dags.pwdb import DAG_NAME
from tests.dags import TEST_AIRFLOW_DAG_FOLDER

logger = logging.getLogger(__name__)


class Test_PWDB_DAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dagbag = DagBag(dag_folder=TEST_AIRFLOW_DAG_FOLDER, include_examples=False,
                            read_dags_from_db=False)

    def test_pwdb_has_two_tasks_and_order(self):
        dag = self.dagbag.get_dag(dag_id=DAG_NAME)
        assert self.dagbag.import_errors == {}
        assert dag is not None
        tasks = dag.tasks
        task_ids = list(map(lambda task: task.task_id, tasks))
        self.assertListEqual(sorted(task_ids), sorted(['download_and_split', 'execute_worker_dags']))

        download_and_split_task = dag.get_task('download_and_split')
        upstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.upstream_list))
        self.assertListEqual(upstream_task_ids, [])
        downstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.downstream_list))
        self.assertListEqual(sorted(downstream_task_ids), sorted(['execute_worker_dags']))

        execute_worker_dags_task = dag.get_task('execute_worker_dags')
        upstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.upstream_list))
        self.assertListEqual(upstream_task_ids, ['download_and_split'])
        downstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.downstream_list))
        self.assertListEqual(sorted(downstream_task_ids), [])

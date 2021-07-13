from datetime import datetime, timedelta

import logging

from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid.adapters.dag.dag_factory import DagFactory, DagPipelineManager
from sem_covid.adapters.dag.dag_pipeline_abc import DagPipeline
from sem_covid.entrypoints import dag_name

logger = logging.getLogger(__name__)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 16),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500)
}

MASTER_DAG_NAME = dag_name(category="debug", name="new_dag_abs_master", version_major=0, version_minor=1)
SLAVE_DAG_NAME = dag_name(category="debug", name="new_dag_abs_worker", version_major=0, version_minor=1)
DAG_NAME = dag_name(category="debug", name="new_dag_abs_architecture", version_major=0, version_minor=1)


class DebugMasterDag(DagPipeline):

    def __init__(self, param):
        self.param = param

    def prepare_terrain_for_workers(self, *args, **kwargs):
        logger.info("---------Start prepare terrain for workers--------")
        logger.info("Param : " + self.param)
        logger.info("---------Stop prepare terrain for workers---------")

    def wakeup_workers(self, *args, **kwargs):
        logger.info("---------Start wakeup workers--------")
        logger.info("Param : " + self.param)
        for i in range(1, 100):
            TriggerDagRunOperator(
                task_id='Worker_debug_' + str(i),
                trigger_dag_id=SLAVE_DAG_NAME,
                conf={"worker_id": i}
            ).execute(kwargs)
        logger.info("---------Stop wakeup workers---------")

    def get_steps(self) -> list:
        return [self.prepare_terrain_for_workers, self.wakeup_workers]


class DebugSlaveDag(DagPipeline):
    def __init__(self, param):
        self.param = param

    def start_work(self, *args, **kwargs):
        if "worker_id" not in kwargs['dag_run'].conf:
            logger.error(
                "Could not find the worker_id in the provided configuration. This DAG is to be triggered by its parent only.")
            return
        worker_id = kwargs['dag_run'].conf['worker_id']
        logger.info("---------Start work for work_id =" + str(worker_id) + "-------")
        logger.info("Param : " + self.param)

    def stop_work(self, *args, **kwargs):
        if "worker_id" not in kwargs['dag_run'].conf:
            logger.error(
                "Could not find the worker_id in the provided configuration. This DAG is to be triggered by its parent only.")
            return
        worker_id = kwargs['dag_run'].conf['worker_id']
        logger.info("---------Stop work for work_id =" + str(worker_id) + "-------")
        logger.info("Param : " + self.param)

    def get_steps(self) -> list:
        return [self.start_work, self.stop_work]


class TestPipeline(DagPipeline):

    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def check_step_1(self, *args, **kwargs):
        logger.info("Hello from step1" + self.param1 + self.param2)

    def check_step_2(self, *args, **kwargs):
        logger.info("Hello from step2" + self.param1 + self.param2)

    def get_steps(self) -> list:
        return [self.check_step_1, self.check_step_2]


dag_factory = DagFactory(DagPipelineManager(TestPipeline(param1="Stefan Architecture", param2=" Yay, all works")),
                         dag_name=DAG_NAME, default_dag_args=default_args)

dag = dag_factory.create_dag()

master_dag = DagFactory(DagPipelineManager(DebugMasterDag(param="MasterDag param  -- SATURN")),
                        dag_name=MASTER_DAG_NAME, default_dag_args=default_args
                        ).create_dag()
slave_dag = DagFactory(DagPipelineManager(DebugSlaveDag(param="SlaveDag param  -- PLUTO")),
                       dag_name=SLAVE_DAG_NAME, default_dag_args=default_args
                       ).create_dag()

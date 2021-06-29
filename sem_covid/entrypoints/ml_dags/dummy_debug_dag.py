from datetime import datetime, timedelta

import logging

from sem_covid.adapters.dag_factory import DagFactory, DagPipelineManager, DagPipeline

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

VERSION = '0.0.1'
DATASET_NAME = 'new_dag_abstraction'
DAG_TYPE = 'debug'
DAG_NAME = "_".join([DAG_TYPE, DATASET_NAME, VERSION])


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
                         dag_name=DAG_NAME, default_args=default_args)

dag = dag_factory.create()

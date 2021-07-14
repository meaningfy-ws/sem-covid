import logging

from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.adapters.dag.abstract_dag_pipeline import DagPipeline
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import CellarDagMaster
from sem_covid.entrypoints.etl_dags.ds_cellar_covid_dags import EU_CELLAR_CORE_KEY, EU_CELLAR_EXTENDED_KEY
from sem_covid.services.sparq_query_registry import QueryRegistry
from sem_covid.services.store_registry import StoreRegistry

logger = logging.getLogger(__name__)

MASTER_DAG_NAME = dag_name(category="debug", name="new_dag_abs_master", version_major=0, version_minor=5)
SLAVE_DAG_NAME = dag_name(category="debug", name="new_dag_abs_worker", version_major=0, version_minor=6)
DAG_NAME = dag_name(category="debug", name="new_dag_abs_architecture", version_major=0, version_minor=7)


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


dag = DagFactory(dag_pipeline=TestPipeline(param1="Stefan Architecture", param2=" Yay, all works"),
                 dag_name=DAG_NAME).create_dag()

master_dag = DagFactory(DebugMasterDag(param="MasterDag param  -- SATURN"),
                        dag_name=MASTER_DAG_NAME).create_dag()

slave_dag = DagFactory(DebugSlaveDag(param="SlaveDag param  -- PLUTO"),
                       dag_name=SLAVE_DAG_NAME, ).create_dag()

# globals()[DAG_NAME] = dag
# globals()[MASTER_DAG_NAME] = master_dag
# globals()[SLAVE_DAG_NAME] = slave_dag

# gigi_dag = DagFactory(
#     CellarDagMaster(
#         list_of_queries=[QueryRegistry().SEM_COVID_CORE_SELECTOR, QueryRegistry().SEM_COVID_EXTENDED_SELECTOR],
#         list_of_query_flags=[EU_CELLAR_CORE_KEY, EU_CELLAR_EXTENDED_KEY],
#         worker_dag_name="WORKER_DAG_NAME",
#         sparql_endpoint_url=config.EU_CELLAR_SPARQL_URL,
#         minio_bucket_name=config.EU_CELLAR_BUCKET_NAME,
#         store_registry=StoreRegistryManager()
#     ), dag_name="MASTER_DAG_NAME").create_dag(schedule_interval="@once",
#                                             max_active_runs=1, concurrency=1)

MINOR = 3
MAJOR = 3

MASTER_DAG_NAME_2 = dag_name(category="etl", name="eu_cellar_covid_1", role="master", version_major=MAJOR,
                           version_minor=MINOR)
WORKER_DAG_NAME_2 = dag_name(category="etl", name="eu_cellar_covid_2", role="worker", version_major=MAJOR,
                           version_minor=MINOR)
dag_master_pipeline = CellarDagMaster(
    list_of_queries=[QueryRegistry().SEM_COVID_CORE_SELECTOR, QueryRegistry().SEM_COVID_EXTENDED_SELECTOR],
    list_of_query_flags=[EU_CELLAR_CORE_KEY, EU_CELLAR_EXTENDED_KEY],
    worker_dag_name=WORKER_DAG_NAME_2,
    sparql_endpoint_url=config.EU_CELLAR_SPARQL_URL,
    minio_bucket_name=config.EU_CELLAR_BUCKET_NAME,
    store_registry=StoreRegistry()
)

test_cellar_covid_dag = DagFactory(
    dag_pipeline=dag_master_pipeline, dag_name=MASTER_DAG_NAME_2).create_dag(schedule_interval="@once",
                                                                           max_active_runs=1, concurrency=1)

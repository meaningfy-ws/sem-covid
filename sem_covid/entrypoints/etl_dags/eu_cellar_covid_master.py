import logging

from sem_covid import config
from sem_covid.adapters.dag.dag_factory import DagFactory, DagPipelineManager
from sem_covid.entrypoints import dag_name, DEFAULT_DAG_ARGUMENTS
from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import CellarDagMaster
from sem_covid.services.sparq_query_registry import QueryRegistry
from sem_covid.services.store_registry import StoreRegistryManager

logger = logging.getLogger(__name__)

DAG_NAME = dag_name(category="etl", name="eu_cellar_covid", version_major=1, version_minor=1)

EU_CELLAR_CORE_KEY = "eu_cellar_core"
EU_CELLAR_EXTENDED_KEY = "eu_cellar_extended"

cellar_dag_master_pipeline = CellarDagMaster(
    list_of_queries=[QueryRegistry().SEM_COVID_CORE_SELECTOR, QueryRegistry().SEM_COVID_EXTENDED_SELECTOR],
    list_of_query_flags=[EU_CELLAR_CORE_KEY, EU_CELLAR_EXTENDED_KEY],
    sparql_endpoint_url=config.EU_CELLAR_SPARQL_URL,
    minio_bucket_name=config.EU_CELLAR_BUCKET_NAME,
    store_registry=StoreRegistryManager()
)

master_dag = DagFactory(
    dag_pipeline=cellar_dag_master_pipeline, dag_name=DAG_NAME,
    default_dag_args=DEFAULT_DAG_ARGUMENTS).create_dag(schedule_interval="@once", max_active_runs=1, concurrency=1)

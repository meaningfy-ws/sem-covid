#!/usr/bin/python3

# lr_etl_finreg_splitter.py
# Date:  20.10.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
import logging
import airflow
from sem_covid.adapters.dag.dag_factory import DagFactory
from sem_covid.entrypoints import dag_name
from sem_covid.entrypoints.notebooks.legal_radar.entrypoints.etl_dags.faiss_multi_indexing_pipeline import \
    FAISSMultipleIndexingPipeline
from sem_covid.entrypoints.notebooks.legal_radar.entrypoints.etl_dags.variable_window_split_documents_pipeline import \
    VariableWindowSplitPipeline

logger = logging.getLogger(__name__)
logger.debug(f"This line is important for DAG discovery because the *airflow module* "
             f"shall be imported here. Otherwise it does not discover DAGs in this "
             f"module. Airflow version {airflow.__version__}")

MINOR = 1
MAJOR = 1
CATEGORY = "etl_legal_radar"

# FinReg windowed splitter DAG

FIN_REG_WINDOWED_SPLITTER_DAG = dag_name(category=CATEGORY, name="finreg_windowed_splitter_dag", version_major=MAJOR,
                                         version_minor=MINOR)

fin_reg_windowed_splitter_dag_pipeline = VariableWindowSplitPipeline()

fin_reg_windowed_splitter_dag = DagFactory(
    dag_pipeline=fin_reg_windowed_splitter_dag_pipeline, dag_name=FIN_REG_WINDOWED_SPLITTER_DAG).create_dag(
    schedule_interval="@once",
    max_active_runs=1, concurrency=1)

# FAISS multiple indexing DAG

FAISS_MULTIPLE_INDEXING_DAG_NAME = dag_name(category=CATEGORY, name="finreg_parts_faiss_indexing_dag",
                                            version_major=MAJOR,
                                            version_minor=MINOR)

faiss_multiple_indexing_pipeline = FAISSMultipleIndexingPipeline()

faiss_multiple_indexing_dag = DagFactory(
    dag_pipeline=faiss_multiple_indexing_pipeline, dag_name=FAISS_MULTIPLE_INDEXING_DAG_NAME).create_dag(
    schedule_interval="@once",
    max_active_runs=1, concurrency=1)

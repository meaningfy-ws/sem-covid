#!/usr/bin/python3

# conftest.py
# Date:  03/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    Provide teh necessary Airflow magic so that it is easy to test the production DAGs.
"""
import logging
import os
from pathlib import Path

import pytest
from airflow.models import DagBag
from airflow.utils import db

SRC_AIRFLOW_DAG_FOLDER = Path(__file__).parent.parent.parent / "sem_covid/"

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def airflow_dag_bag():
    logger.info(f"Changing the AIRFLOW_HOME variable to {SRC_AIRFLOW_DAG_FOLDER}")
    # changing the AIRFLOW_HOME environment variable to current code
    os.environ["AIRFLOW_HOME"] = str(SRC_AIRFLOW_DAG_FOLDER)
    # Initialising the Airflow DB so that it works properly with the new AIRFLOW_HOME
    logger.info(f"Recreating the Airflow Database")
    db.resetdb()
    db.initdb()
    logger.info(f"Instantiating the Airflow DagBag for testing prod DAGs")
    dag_bag = DagBag(dag_folder=SRC_AIRFLOW_DAG_FOLDER, include_examples=False,
                     read_dags_from_db=False)
    return dag_bag

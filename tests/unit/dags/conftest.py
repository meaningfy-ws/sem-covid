#!/usr/bin/python3

# conftest.py
# Date:  03/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    Provide teh necessary Airflow magic so that it is easy to test the production DAGs.
"""
import json
import logging
import os
import pathlib
from pathlib import Path

import pytest
from SPARQLWrapper import SPARQLWrapper
from airflow.models import DagBag
from airflow.utils import db

SRC_AIRFLOW_DAG_FOLDER = Path(__file__).parent.parent.parent.parent / "sem_covid/"
TEST_DATA_FOLDER = pathlib.Path(__file__).parent.parent.parent / "test_data"

logger = logging.getLogger(__name__)


class FakeSPARQL(SPARQLWrapper):
    def __init__(self):
        self._query = 'No query'

    def setQuery(self, query):
        self._query = query

    def setReturnFormat(self, text):
        return True

    def query(self):
        return self

    def convert(self):
        return self._query


@pytest.fixture(scope="session")
def airflow_dag_bag():
    logger.info(f"Changing the AIRFLOW_HOME variable to {SRC_AIRFLOW_DAG_FOLDER}")
    # changing the AIRFLOW_HOME environment variable to current code
    os.environ["AIRFLOW_HOME"] = str(SRC_AIRFLOW_DAG_FOLDER)
    os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
    # Initialising the Airflow DB so that it works properly with the new AIRFLOW_HOME
    logger.info(f"Recreating the Airflow Database")
    db.resetdb()
    db.initdb()
    logger.info(f"Instantiating the Airflow DagBag for testing prod DAGs")
    dag_bag = DagBag(dag_folder=SRC_AIRFLOW_DAG_FOLDER, include_examples=False,
                     read_dags_from_db=False)
    logger.info(f"The DAG bag contains teh following ids: {dag_bag.dag_ids}")
    return dag_bag


@pytest.fixture(scope="session")
def fragment1_eu_cellar_covid() -> pathlib.Path:
    path = TEST_DATA_FOLDER / "eu_cellar_covid_fragments" / "402fa68a01a26b690c0f098278185c180fe06ea53ed3b3a30f6020482816e1e7.json"
    return json.loads(path.read_bytes())


@pytest.fixture(scope="session")
def fragment2_eu_cellar_covid() -> pathlib.Path:
    path = TEST_DATA_FOLDER / "eu_cellar_covid_fragments" / "a54b90e91baa9171814668f1c764a04f35d31a61b8f8b02e0532968a9c1d71e3.json"
    return json.loads(path.read_bytes())


@pytest.fixture(scope="session")
def fragment3_eu_cellar_covid() -> pathlib.Path:
    path = TEST_DATA_FOLDER / "eu_cellar_covid_fragments" / "db9f1053db03dd74d0134ceee8f166a3c77d8079cd065b73bcaa113556655e7c.json"
    return json.loads(path.read_bytes())


@pytest.fixture(scope="session")
def fragment4_eu_cellar_covid() -> pathlib.Path:
    path = TEST_DATA_FOLDER / "eu_cellar_covid_fragments" / "f590e79d741fe971418c0fda170c0f17eabc86013a7166641b231896b969a6be.json"
    return json.loads(path.read_bytes())


@pytest.fixture(scope="session")
def get_spaqrl_result_set_fetched_as_tabular():
    path = TEST_DATA_FOLDER / "eu_cellar_covid_fragments" / "unified_eu_cellar_fragment.json"
    return json.loads(path.read_bytes())

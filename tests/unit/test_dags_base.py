#!/usr/bin/python3

# test_dags_base.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

from airflow.models import DagBag
from pytest import fixture


@fixture
def dag_env():
    return DagBag()


def test_ml_process_dag(dag_env):
    assert not dag_env.import_errors

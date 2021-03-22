#!/usr/bin/python3

# test_dags_base.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import logging

from airflow.models import DagBag
from pytest import fixture

logger = logging.getLogger(__name__)


@fixture
def dag_env():
    return DagBag(include_examples=False)


def test_loading_dags(dag_env):
    pass


def test_ml_process_dag(dag_env):
    assert not dag_env.import_errors


def test_kw_injection():
    def f(**kwargs):
        kwargs["x"] = kwargs.get("x", 5)
        return kwargs

    assert f(x=10)["x"] == 10
    assert f()["x"] == 5

#!/usr/bin/python3

# test_dags_base.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import logging
from datetime import datetime

from airflow import DAG
from pytest import fixture

from ml_experiments.services.dummy_experiment import DummyExperiment

logger = logging.getLogger(__name__)


@fixture(scope="session")
def dummy_experiment_dag():
    return DummyExperiment().create_dag(start_date=datetime.now())


def test_dummy_dag_creation(dummy_experiment_dag):
    assert isinstance(dummy_experiment_dag, DAG)
    assert "DummyExperiment" in dummy_experiment_dag.dag_id


def test_dummy_dag_anatomy(dummy_experiment_dag):
    assert dummy_experiment_dag.default_args
    assert len(dummy_experiment_dag.task_ids) == 6
    assert 'model_training_step' in dummy_experiment_dag.task_ids
    model_training_step = dummy_experiment_dag.get_task('model_training_step')
    assert 'model_evaluation_step' in model_training_step.downstream_task_ids
    assert 'data_preparation_step' in model_training_step.upstream_task_ids


def test_kw_injection():
    def f(**kwargs):
        kwargs["x"] = kwargs.get("x", 5)
        return kwargs

    assert f(x=10)["x"] == 10
    assert f()["x"] == 5


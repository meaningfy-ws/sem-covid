#!/usr/bin/python3

# dag_template.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
This is a DAG template for the generic ML MLOps level 1.
It is inspired from [this article](https://cloud.google.com/solutions/machine-learning/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import task, get_current_context

DAG_IDENTIFIER = "change_me"
VERSION = "0.0.1"

DEFAULT_ARGS = {
    "owner": "Meaningfy",
    "depends_on_past": False,
    "retries": 0,
}

# running the DAG as a context manager

with DAG(DAG_IDENTIFIER + VERSION,
         default_args=DEFAULT_ARGS,
         schedule_interval="@once",
         max_active_runs=1,
         concurrency=1) as dag:

    @task(multiple_outputs=True)
    def data_extraction(raw_json: str):
        raise NotImplementedError

    @task(multiple_outputs=True)
    def data_validation():
        raise NotImplementedError

#

import logging
from airflow import DAG

logger = logging.getLogger(__name__)


class MLProcessDAG(DAG):
    def __init__(self, *args, **kwargs):
        super(MLProcessDAG, self).__init__(*args, **kwargs)
        self.default_args = self.build_default_args(kwargs)

    def build_default_args(self, kwargs):
        fixed_defaults_args = {
            'owner': 'Meaningfy',
            'schedule_interval': '@once',
            'max_active_runs': 1,
            'concurrency': 1,
            "retries": 0,
            'depends_on_past': False,
        }
        fixed_defaults_args.update(kwargs.get('default_args', {}))
        return fixed_defaults_args


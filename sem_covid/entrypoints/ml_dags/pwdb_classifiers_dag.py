#!/usr/bin/python3

# pwdb_classifiers_dag.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to initialize a DAG
    for the process of training classifiers based on the PWDB dataset.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from sem_covid.entrypoints import dag_name
from sem_covid.services.ml_pipelines.pwdb_classifiers_pipeline import PWDBClassifiers

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

DAG_NAME = dag_name(category='ml', name='pwdb_classifiers', version_minor=0, version_major=1)

with DAG(DAG_NAME,
         default_args=default_args,
         schedule_interval="@once",
         max_active_runs=1,
         concurrency=1) as dag:
    feature_engineering = PythonOperator(task_id=f"feature_engineering",
                                         python_callable=PWDBClassifiers.feature_engineering,
                                         retries=1,
                                         dag=dag
                                         )

    model_training = PythonOperator(task_id=f"model_training",
                                    python_callable=PWDBClassifiers.model_training,
                                    retries=1,
                                    dag=dag
                                    )

    feature_engineering >> model_training

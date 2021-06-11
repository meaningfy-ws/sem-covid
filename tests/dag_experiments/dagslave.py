#!/usr/bin/python3

# dummy_test_dag.py
# Date:  06/05/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This DAG module has the purpose of designing some experimental DAG architectures
"""
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'Meaningfy',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

with DAG('slave_architecture_test_006', start_date=datetime(2020, 5, 15), schedule_interval='@once',
         default_args=default_args, max_active_runs=4,
         concurrency=8) as dag:
    def task1_callable():
        pass


    def task2_callable(**context):
        dag_run_conf = context['dag_run'].conf
        logger.info(str(dag_run_conf))

    task1 = PythonOperator(task_id='task1',
                           python_callable=task1_callable, retries=1)
    task2 = PythonOperator(task_id='task2',
                           python_callable=task2_callable, retries=1, provide_context=True)

    task1 >> task2

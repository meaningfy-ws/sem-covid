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
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.task_group import TaskGroup

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

with DAG('master_architecture_test_006', start_date=datetime(2020, 5, 15), schedule_interval='@once',
         default_args=default_args, max_active_runs=1, concurrency=4) as dag:
    def task1_callable():
        logger.info("In task1")


    def task2_callable():
        logger.info("In task2")


    task1 = PythonOperator(task_id='task1',
                           python_callable=task1_callable, retries=1, dag=dag)
    task2 = PythonOperator(task_id='task2',
                           python_callable=task2_callable, retries=1, dag=dag)
    task1 >> task2
    with TaskGroup("group_of_parallel_tasks") as group1:
        for i in range(1000):
            trigger_subdag = TriggerDagRunOperator(
                task_id='trigger_slave_dag_' + str(i),
                trigger_dag_id='slave_architecture_test_006',
                conf={"filename": str(i)}
            )

            task2 >> trigger_subdag

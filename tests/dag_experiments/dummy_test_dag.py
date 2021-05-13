#!/usr/bin/python3

# dummy_test_dag.py
# Date:  06/05/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This DAG module has the purpose of designing some experi-mental DAG architectures
"""

import logging
from datetime import datetime, timedelta
from random import randrange, choice

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
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

with DAG('dag_architecture_test_v.0.10', start_date=datetime(2020, 5, 15), schedule_interval='@once',
         default_args=default_args, ) as dag:
    def exec_task_function(task_id_param: int):
        logger.info(f"This is a task with input {id}")
        if choice([True, False]):
            raise RuntimeError("This is a random error")


    @dag.task
    def exec_task(task_id_param: int):
        exec_task_function(task_id_param)


    def task_selector(param: int):
        r = randrange(1000, 2000)
        logger.info(f"The range of tasks is {r}")
        for task_id in range(r):
            yield task_id


    task_after = DummyOperator(task_id="task_after")
    task_before = DummyOperator(task_id="task_before")

    # Avoid generating this list dynamically to keep DAG topology stable between DAG runs

    with TaskGroup("group_of_parallel_tasks") as group1:
        for t in task_selector(10):
            task1 = PythonOperator(python_callable=exec_task_function, op_kwargs={"task_id_param":t}, task_id=f'enrich_{t}')
            task2 = PythonOperator(python_callable=exec_task_function, op_kwargs={"task_id_param": t},
                           task_id=f'tika_{t}')
            task3 = PythonOperator(python_callable=exec_task_function, op_kwargs={"task_id_param": t},
                           task_id=f'elasticsearch{t}')
            task1 >> task2 >> task3

    task_before >> group1 >> task_after

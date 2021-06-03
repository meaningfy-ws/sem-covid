import random
import time
from datetime import datetime, timedelta

import airflow
import airflow.utils.helpers
from airflow.models import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.subdag import SubDagOperator

# args and params
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(year=2018, month=7, day=10),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
    "catchup": False
}

dag_id_parent = 'simplified_parent_dag_v1'
dag_id_child_prefix = 'child_dag_'

tid_prefix_check = 'check_'
tid_prefix_spark = 'spark_submit_'
tid_prefix_subdag = 'subdag_'

db_names = ['db_1', 'db_2', 'db_3']


# helper methods
def mimic_task(task_name, success_percent=100, sleep_duration=0):
    time.sleep(sleep_duration)
    if (random.randint(1, 101) <= success_percent):
        print('%s succeeded' % (task_name))
        return True
    else:
        print('%s failed' % (task_name))
        return False


# callable methods
def check_sync_enabled(db_name, **kwargs):
    if mimic_task('check_sync_enabled for %s' % db_name, 70, 1) == False:
        raise Exception('Exception in check_sync_enabled for %s' % db_name)


def spark_submit(db_name, **kwargs):
    if mimic_task('spark_submit for %s' % db_name, 60, 5) == False:
        raise Exception('Exception in spark_submit for %s' % db_name)


# subdag creation
def create_subdag(dag_parent, dag_id_child_prefix, db_name):
    # dag params
    dag_id_child = '%s.%s' % (dag_parent.dag_id, dag_id_child_prefix + db_name)
    default_args_copy = default_args.copy()

    # dag
    dag = DAG(dag_id=dag_id_child,
              default_args=default_args_copy,
              schedule_interval=None)

    # operators
    tid_check = tid_prefix_check + db_name
    py_op_check = PythonOperator(task_id=tid_check, dag=dag,
                                 python_callable=check_sync_enabled,
                                 op_args=[db_name])

    tid_spark = tid_prefix_spark + db_name
    py_op_spark = PythonOperator(task_id=tid_spark, dag=dag,
                                 python_callable=spark_submit,
                                 op_args=[db_name])

    py_op_check >> py_op_spark
    return dag


def create_subdag_operator(dag_parent, db_name):
    tid_subdag = tid_prefix_subdag + db_name
    subdag = create_subdag(dag_parent, tid_prefix_subdag, db_name)
    sd_op = SubDagOperator(task_id=tid_subdag, dag=dag_parent, subdag=subdag)
    return sd_op


def create_subdag_operators(dag_parent, db_names):
    subdags = [create_subdag_operator(dag_parent, db_name) for db_name in db_names]
    # chain subdag-operators together
    airflow.models.baseoperator.chain(*subdags)
    return subdags


# (top-level) DAG & operators
dag = DAG(dag_id=dag_id_parent,
          default_args=default_args,
          schedule_interval=None)

subdag_ops = create_subdag_operators(dag, db_names)

dummy_op_start = DummyOperator(task_id='dummy_op_start', dag=dag)
dummy_op_start >> subdag_ops[0]

dummy_op_end = DummyOperator(task_id='dummy_op_end', dag=dag)
subdag_ops[-1] >> dummy_op_end

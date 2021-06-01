from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from sem_covid.services.pwdb_random_forest_experiment import RandomForestPWDBExperiment

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

VERSION = '0.0.1'
CATEGORY = 'target_group_l1'
CLASSIFIER = 'random_forest'
DATASET_NAME = 'pwdb'
DAG_TYPE = 'ml'
DAG_NAME = "_".join([DAG_TYPE, DATASET_NAME, CLASSIFIER, CATEGORY, VERSION])

with DAG(DAG_NAME,
         default_args=default_args,
         schedule_interval="@once",
         max_active_runs=1,
         concurrency=1) as dag:
    feature_engineering = PythonOperator(task_id=f"feature_engineering",
                                         python_callable=RandomForestPWDBExperiment.feature_engineering,
                                         retries=1,
                                         dag=dag
                                         )

    model_training = PythonOperator(task_id=f"model_training",
                                    python_callable=RandomForestPWDBExperiment.model_training,
                                    retries=1,
                                    dag=dag
                                    )

    feature_engineering >> model_training

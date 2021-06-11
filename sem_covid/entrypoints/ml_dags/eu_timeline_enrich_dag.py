from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta

from sem_covid.services.enrich_pipelines.eu_timeline_enrich_pipeline import EuTimeLineEnrich

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
DAG_TYPE = 'ml'
OPERATION = 'enrichment'
DATASET_NAME = 'eu_timeline'
DAG_NAME = "_".join([DAG_TYPE, DATASET_NAME, OPERATION, VERSION])

with DAG(DAG_NAME,
         default_args=default_args,
         schedule_interval="@once",
         max_active_runs=1,
         concurrency=1) as dag:
    dataset_preparation = PythonOperator(task_id=f"dataset_preparation",
                                         python_callable=EuTimeLineEnrich.prepare_dataset,
                                         retries=1,
                                         dag=dag
                                         )

    dataset_enrichment = PythonOperator(task_id=f"dataset_enrichment",
                                        python_callable=EuTimeLineEnrich.enrich_dataset,
                                        retries=1,
                                        dag=dag
                                        )

    dataset_preparation >> dataset_enrichment

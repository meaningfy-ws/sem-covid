"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator

import hashlib
import json
import pathlib
from functools import partial
from multiprocessing import Pool, cpu_count
import requests

def enrich_policy_watch():
    with open(pathlib.Path('resources') / 'covid19db.json', encoding='utf-8') as covid19db:
        covid19json = json.loads(covid19db.read())

    list_count = len(covid19json)
    current_item = 0

    for field_data in covid19json:
        current_item += 1
        print('[' + str(current_item) + ' / ' + str(list_count) + '] - ' + field_data['fieldData']['title'])
        # map.pool has SERIOUS LOCK/DEADLOCK ISSUES ! Remove the code and make it sequential !
        with Pool(processes=cpu_count()) as pool:
            field_data['portalData']['sources'] = pool.map(partial(__download_source),
                                                           field_data['portalData']['sources'])
            pool.close()
            pool.join()

            for source in field_data['portalData']['sources']:
                with open(pathlib.Path('resources/policy_watch_field_data_fragments') / hashlib.sha256(
                        source['sources::url'].encode('utf-8')).hexdigest(), 'w') as enriched_fragment_file:
                    json.dump(source, enriched_fragment_file)


def __download_source(source):
    try:
        url = source['sources::url'] if source['sources::url'].startswith('http') else (
                'http://' + source['sources::url'])
        request = requests.get(url, allow_redirects=True)

        source['content'] = str(request.content)
    except Exception as ex:
        source['failure_reason'] = str(ex)

    return source
    
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2015, 6, 1),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("python_test_001", default_args=default_args, schedule_interval=timedelta(minutes=1000))

python_task=PythonOperator(task_id='my_test_task_001', python_callable=enrich_policy_watch, retries=1, dag=dag)

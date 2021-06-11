#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
from SPARQLWrapper import SPARQLWrapper

from sem_covid.entrypoints.etl_dags.treaties import get_single_item, make_request
from sem_covid.entrypoints.etl_dags.treaties_worker import DAG_NAME
from tests.unit.test_store.fake_storage import FakeObjectStore


def test_treaties_worker_has_three_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert airflow_dag_bag.import_errors == {}
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'Enrich', 'Tika', 'Elasticsearch'}.issubset(set(task_ids))

    enrich_task = dag.get_task('Enrich')
    upstream_task_id = list(map(lambda task: task.task_id, enrich_task.upstream_list))
    assert not upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, enrich_task.downstream_list))
    assert 'Tika' in downstream_task_id

    tika_task = dag.get_task('Tika')
    upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
    assert 'Enrich' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
    assert 'Elasticsearch' in downstream_task_id

    elastic_search_task = dag.get_task('Elasticsearch')
    upstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.upstream_list))
    assert 'Tika' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.downstream_list))
    assert not downstream_task_id


class FakeSPARQL(SPARQLWrapper):
    def __init__(self):
        self._query = 'No query'

    def setQuery(self, query):
        self._query = query

    def setReturnFormat(self, text):
        return True

    def query(self):
        return self

    def convert(self):
        return self._query


def test_get_single_item():
    json_file_name = 'file_name'
    my_response = {
        'document_one': 'one',
        'document_two': 'two'
    }
    query = {
        'results': {
            'bindings': my_response
        }
    }
    response = get_single_item(query, json_file_name, FakeSPARQL(), FakeObjectStore())
    assert response == my_response


def test_make_request():
    query = 'select'
    response = make_request(query, FakeSPARQL())
    assert response == query

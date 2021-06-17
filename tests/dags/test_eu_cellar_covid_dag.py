#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
import re

from SPARQLWrapper import SPARQLWrapper

from sem_covid.entrypoints.etl_dags.eu_cellar_covid import DAG_NAME, make_request, get_single_item, EURLEX_QUERY, \
    EURLEX_EXTENDED_QUERY, convert_key, add_document_source_key
from sem_covid.entrypoints.etl_dags.eu_cellar_covid_worker import content_cleanup
from tests.dags.conftest import FakeSPARQL
from tests.unit.test_store.fake_storage import FakeObjectStore


def test_eurlex_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'download_and_split', 'execute_worker_dags'}.issubset(set(task_ids))

    download_and_split_task = dag.get_task('download_and_split')
    upstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.upstream_list))
    assert not upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.downstream_list))
    assert 'execute_worker_dags' in downstream_task_ids

    execute_worker_dags_task = dag.get_task('execute_worker_dags')
    upstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.upstream_list))
    assert 'download_and_split' in upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.downstream_list))
    assert not downstream_task_ids


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
    response = get_single_item(query, json_file_name, FakeSPARQL(), FakeObjectStore(), lambda x: x)
    assert response == my_response


def test_make_request():
    query = 'select'
    response = make_request(query, FakeSPARQL())
    assert response == query


def test_sparql_query_make_request_core():
    result = make_request(EURLEX_QUERY, FakeSPARQL())
    assert result


def test_sparql_query_make_request_ext():
    result = make_request(EURLEX_EXTENDED_QUERY, FakeSPARQL())
    assert result


def test_access_to_resources(fragment1_eu_cellar_covid,
                             fragment2_eu_cellar_covid,
                             fragment3_eu_cellar_covid,
                             fragment4_eu_cellar_covid):
    assert fragment1_eu_cellar_covid["work"] and fragment1_eu_cellar_covid["content"]
    assert fragment2_eu_cellar_covid["work"] and not fragment2_eu_cellar_covid["content"]
    assert fragment3_eu_cellar_covid["work"] and fragment3_eu_cellar_covid["content"]
    assert fragment4_eu_cellar_covid["work"] and fragment4_eu_cellar_covid["content"]


def test_text_cleanup(fragment3_eu_cellar_covid):
    content3 = content_cleanup(fragment3_eu_cellar_covid["content"])
    assert "\n" not in content3
    assert "á" not in content3
    assert "—" not in content3
    assert "\u2014" not in content3
    assert b"\u2014".decode("utf-8") not in content3
    assert not re.match(r"\s\s", content3)


def test_convert_key():
    result = convert_key("Extended EurLex part 1")
    assert result == "eu_cellar_extended"


def test_add_document_source_key():
    test_dict = {"name": "John", "age": 20}
    add_document_source_key(test_dict, "eu_cellar_extended")
    assert 'eu_cellar_extended' in test_dict
    assert 'eu_cellar_core' in test_dict
    assert test_dict['eu_cellar_extended'] is True
    assert test_dict['eu_cellar_core'] is False

#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

from sem_covid.entrypoints.etl_dags.ds_fin_reg_dags import MASTER_DAG_NAME

def test_finreg_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=MASTER_DAG_NAME)
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


# class FakeSPARQL(SPARQLWrapper):
#     def __init__(self):
#         self._query = 'No query'
#
#     def setQuery(self, query):
#         self._query = query
#
#     def setReturnFormat(self, text):
#         return True
#
#     def query(self):
#         return self
#
#     def convert(self):
#         return self._query
#
#
# def test_get_single_item():
#     json_file_name = 'file_name'
#     my_response = {
#         'document_one': 'one',
#         'document_two': 'two'
#     }
#     query = {
#         'results': {
#             'bindings': my_response
#         }
#     }
#     response = get_single_item(query, json_file_name, FakeSPARQL(), FakeObjectStore())
#     assert response == my_response
#
#
# def test_make_request():
#     query = 'select'
#     response = make_request(query, FakeSPARQL())
#     assert response == query

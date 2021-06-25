#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com


from sem_covid.entrypoints.etl_dags.eu_cellar_covid_worker import DAG_NAME


def test_eurlex_worker_has_three_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'Enrich', 'Tika', 'Content_cleanup', 'Elasticsearch'}.issubset(set(task_ids))

    enrich_task = dag.get_task('Enrich')
    upstream_task_id = list(map(lambda task: task.task_id, enrich_task.upstream_list))
    assert not upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, enrich_task.downstream_list))
    assert 'Tika' in downstream_task_id

    tika_task = dag.get_task('Tika')
    upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
    assert 'Enrich' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
    assert 'Content_cleanup' in downstream_task_id

    tika_task = dag.get_task('Content_cleanup')
    upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
    assert 'Tika' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
    assert 'Elasticsearch' in downstream_task_id

    elastic_search_task = dag.get_task('Elasticsearch')
    upstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.upstream_list))
    assert 'Content_cleanup' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.downstream_list))
    assert not downstream_task_id

#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com


from sem_covid.entrypoints.etl_dags.crawl_eu_action_timeline import DAG_NAME


def test_crawl_eu_action_timeline_has_three_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'extract', 'transform_structure', 'load'}.issubset(set(task_ids))

    crawl_task = dag.get_task('extract')
    upstream_task_id = list(map(lambda task: task.task_id, crawl_task.upstream_list))
    assert not upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, crawl_task.downstream_list))
    assert 'transform_structure' in downstream_task_id

    tika_task = dag.get_task('transform_structure')
    upstream_task_id = list(map(lambda task: task.task_id, tika_task.upstream_list))
    assert 'extract' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, tika_task.downstream_list))
    assert 'load' in downstream_task_id

    elastic_search_task = dag.get_task('load')
    upstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.upstream_list))
    assert 'transform_structure' in upstream_task_id
    downstream_task_id = list(map(lambda task: task.task_id, elastic_search_task.downstream_list))
    assert not downstream_task_id

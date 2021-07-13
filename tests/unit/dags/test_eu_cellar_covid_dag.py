#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

from sem_covid.entrypoints.etl_dags.ds_eu_cellar_covid_dags import MASTER_DAG_NAME


def test_eurlex_has_two_tasks_and_order(airflow_dag_bag):
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

# def test_text_cleanup(fragment3_eu_cellar_covid):
#     content3 = content_cleanup(fragment3_eu_cellar_covid["content"])
#     assert "\n" not in content3
#     assert "á" not in content3
#     assert "—" not in content3
#     assert "\u2014" not in content3
#     assert b"\u2014".decode("utf-8") not in content3
#     assert not re.match(r"\s\s", content3)


# def test_eu_cellar_transformation_rules(get_spaqrl_result_set_fetched_as_tabular):
#     first_element_transformed = transform_eu_cellar_item(get_spaqrl_result_set_fetched_as_tabular[0])
#
#     assert isinstance(first_element_transformed, dict)
#     assert isinstance(first_element_transformed["cdm_types"], list)
#     assert len(first_element_transformed["cdm_types"]) == 2
#     assert len(first_element_transformed["cdm_type_labels"]) == 0

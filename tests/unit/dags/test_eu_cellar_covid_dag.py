#!/usr/bin/python3

# Date:  10/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
import re

import pandas as pd
import pytest

from sem_covid.entrypoints.etl_dags.eu_cellar_covid import DAG_NAME, get_documents_from_triple_store, \
    download_and_split_callable, unify_dataframes_and_mark_source
from sem_covid.entrypoints.etl_dags.eu_cellar_covid_worker import content_cleanup
from sem_covid.services.sc_wrangling.json_transformer import transform_eu_cellar_item
from tests.unit.test_store.fake_storage import FakeTripleStore


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


def test_fetch_documents_from_fake_cellar():
    triple_store = FakeTripleStore()
    docs_df = get_documents_from_triple_store(["dummy query 1", "dummy query 2", "dummy query 3"],
                                              ["flag1", "flag2", "flag3"],
                                              triple_store_adapter=triple_store, id_column='col1')

    assert "flag1" in docs_df.columns and "flag2" in docs_df.columns
    assert docs_df['col1'].is_unique
    assert docs_df.iloc[0]['flag1'] and docs_df.iloc[0]['flag2']

    with pytest.raises(Exception) as e:
        docs_df = get_documents_from_triple_store(["dummy query 1", ], ["flag1", "flag2", "flag3"],
                                                  triple_store_adapter=triple_store, id_column='col1')


def test_download_and_split_callable():
    pass


def test_unify_dataframes_and_mark_source():
    d = {'work': ["A", "B", "D"], 'col2': [3, 4, 8], 'col3': [55, 66, 77]}
    df_test = pd.DataFrame(data=d)
    d2 = {'work': ["A", "C", "E"], 'col2': [5, 6, 9], "col3": [88, 99, 21]}
    df2_test = pd.DataFrame(data=d2)
    list_of_result_data_frames = [df_test, df2_test]
    list_of_query_flags = ["flag1", "flag2"]
    unified_dataframe = unify_dataframes_and_mark_source(list_of_data_frames=list_of_result_data_frames,
                                                         list_of_flags=list_of_query_flags,
                                                         id_column="work")
    assert len(unified_dataframe) == 5
    assert {"flag1", "flag2"}.issubset(set(unified_dataframe.columns))
    assert unified_dataframe.iloc[0]["flag1"] and unified_dataframe.iloc[0]["flag2"]
    assert unified_dataframe.iloc[1]["flag1"] and not unified_dataframe.iloc[1]["flag2"]


def test_eu_cellar_transformation_rules(get_spaqrl_result_set_fetched_as_tabular):
    first_element_transformed = transform_eu_cellar_item(get_spaqrl_result_set_fetched_as_tabular[0])

    assert isinstance(first_element_transformed, dict)
    assert isinstance(first_element_transformed["cdm_types"], list)
    assert len(first_element_transformed["cdm_types"]) == 2
    assert len(first_element_transformed["cdm_type_labels"]) == 0

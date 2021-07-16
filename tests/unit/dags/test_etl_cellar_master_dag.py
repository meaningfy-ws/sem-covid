import pandas as pd
import pytest
from airflow.exceptions import DagNotFound

from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import CellarDagMaster, get_documents_from_triple_store, \
    unify_dataframes_and_mark_source, get_and_transform_documents_from_triple_store
from sem_covid.services.sc_wrangling.json_transformer import transform_eu_cellar_item
from tests.unit.test_store.fake_storage import FakeTripleStore
from tests.unit.test_store.fake_store_registry import FakeStoreRegistry

FAKE_LIST_OF_QUERIES = ['EU_CELLAR_CORE_QUERY', 'EU_CELLAR_EXTENDED_QUERY']
FAKE_LIST_OF_FLAGS = ['EU_CELLAR_CORE_KEY', 'EU_CELLAR_EXTENDED_KEY']
FAKE_EU_CELLAR_SPARQL_URL = "http://fake-url.fake"
FAKE_EU_CELLAR_BUCKET_NAME = "fake-bucket-name"


def test_etl_cellar_master_dag():
    # instantiating the class
    store_registry = FakeStoreRegistry()

    master_dag = CellarDagMaster(list_of_queries=FAKE_LIST_OF_QUERIES, list_of_query_flags=FAKE_LIST_OF_FLAGS,
                                 sparql_endpoint_url=FAKE_EU_CELLAR_SPARQL_URL, worker_dag_name="worker",
                                 minio_bucket_name=FAKE_EU_CELLAR_BUCKET_NAME, store_registry=store_registry)
    dag_steps = master_dag.get_steps()
    master_dag.select_assets()
    minio_client = store_registry.minio_object_store('fake')

    for key, value in minio_client._objects.items():
        assert 'documents' in key
        assert '.json' in key
        assert 'work' in value
        assert 'title' in value

    # test steps
    assert list == type(dag_steps)
    assert 2 == len(dag_steps)
    assert hasattr(dag_steps[0], '__self__')
    assert hasattr(dag_steps[1], '__self__')

    # testing execute
    with pytest.raises(DagNotFound):
        # we test that the work is found and loaded but we don't test triggering in the airflow environment
        master_dag.trigger_workers()


def test_fetch_documents_from_fake_cellar():
    triple_store = FakeTripleStore()

    docs_df = get_documents_from_triple_store(["dummy query 1", "dummy query 2", "dummy query 3"],
                                              ["flag1", "flag2", "flag3"],
                                              triple_store_adapter=triple_store, id_column='work')

    assert "flag1" in docs_df.columns and "flag2" in docs_df.columns
    assert docs_df['work'].is_unique
    assert docs_df.iloc[0]['flag1'] and docs_df.iloc[0]['flag2']

    with pytest.raises(Exception) as e:
        docs_df = get_documents_from_triple_store(["dummy query 1", ], ["flag1", "flag2", "flag3"],
                                                  triple_store_adapter=triple_store, id_column='work')


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


def test_get_and_transform_documents_from_triple_store():
    triple_store = FakeTripleStore()

    list_of_queries = ["dummy query 1", "dummy query 2", "dummy query 3"]
    list_of_query_flags = ["flag1", "flag2", "flag3"]
    id_column = 'work'

    result = get_and_transform_documents_from_triple_store(list_of_queries=list_of_queries,
                                                           triple_store_adapter=triple_store,
                                                           transformation_function=transform_eu_cellar_item)

    print(result[0].iloc[0])

    assert isinstance(result, list)
    assert isinstance(result[0], pd.DataFrame)
    assert 1 == len(result[0].iloc[0]["title"])
    assert "COMMISSION" in result[0].iloc[0]["title"][0]

    assert "dossiers" in result[0].columns
    assert not result[0].iloc[0]["dossiers"]

    data = {'work': 'http://publications.europa.eu/resource/cellar/fea565f4-e1f9-11ea-ad25-01aa75ed71a1',
            'title': ['Commission proposal for a Council Recommendation on a Child Guarantee'], 'cdm_types': None,
            'cdm_type_labels': None, 'resource_types': None, 'resource_type_labels': None, 'eurovoc_concepts': None,
            'eurovoc_concept_labels': None, 'subject_matters': None, 'subject_matter_labels': None, 'directory_codes': None,
            'directory_codes_labels': None, 'celex_numbers': None, 'legal_elis': None, 'id_documents': None, 'same_as_uris': None,
            'authors': None, 'author_labels': None, 'full_ojs': None, 'oj_sectors': None, 'internal_comments': None,
            'is_in_force': None, 'dates_document': None, 'dates_created': None, 'legal_dates_entry_into_force': None,
            'legal_dates_signature': None, 'manifs_pdf': None, 'manifs_html': None, 'pdfs_to_download': None,
            'htmls_to_download': None, 'dossiers': None, 'related_works': None, 'work_sequences': None, 'core': True}

    list_of_result_data_frames = [pd.DataFrame.from_records(data,index=["gfdhfg"])]
    list_of_result_sets = [df.to_dict(orient="records") for df in list_of_result_data_frames]
    list_of_transformed_result_sets = [[transform_eu_cellar_item(item_dict) for item_dict in result_set_dict_list] for
                                       result_set_dict_list in list_of_result_sets]
    list_of_transformed_df = [pd.DataFrame.from_records(result_set) for result_set in list_of_transformed_result_sets]

    print(list_of_transformed_df[0])

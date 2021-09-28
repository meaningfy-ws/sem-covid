import great_expectations as ge

from sem_covid import config
from sem_covid.services.dataset_pipelines.unified_dataset_pipeline import SPECIFIC_DATASET_COLUMNS, \
    COMMON_DATASET_COLUMNS
from sem_covid.services.store_registry import store_registry

es_store = store_registry.es_index_store()


TEXT_COLUMNS = ["title", "content", "doc_source", "country", "pwdb_category",
                "pwdb_type_of_measure"]
ARRAY_COLUMNS = ["pwdb_target_group_l1", "pwdb_funding", "pwdb_actors", "document_embeddings",
                 "topic_embeddings"] + SPECIFIC_DATASET_COLUMNS

UNIFIED_DATASET_COLUMNS = COMMON_DATASET_COLUMNS + SPECIFIC_DATASET_COLUMNS

PWDB_CATEGORIES = ['Ensuring business continuity and support for essential services',
                   'Protection of workers, adaptation of workplace',
                   'Supporting businesses to get back to normal',
                   'Reorientation of business activities',
                   'Income protection beyond short-time work',
                   'Employment protection and retention',
                   'Supporting businesses to stay afloat',
                   'Promoting the economic, labour market and social recovery',
                   'Measures to prevent social hardship']


def test_validate_enriched_dataset():
    df_from_elastic = es_store.get_dataframe(index_name=config.UNIFIED_DATASET_ELASTIC_SEARCH_INDEX_NAME)
    gdf = ge.from_pandas(df_from_elastic)
    # contain the defined columns
    assert gdf.expect_table_columns_to_match_set(column_set=UNIFIED_DATASET_COLUMNS,
                                                 exact_match=True).success
    # titles shall not be missing
    assert gdf.expect_column_values_to_not_be_null(column="title").success
    # content shall not be missing
    assert gdf.expect_column_values_to_not_be_null(column="content").success
    # date shall not be missing
    assert gdf.expect_column_values_to_not_be_null(column="date").success
    # title length shall be greater than 5 chars
    assert gdf.expect_column_value_lengths_to_be_between(column="title", min_value=4).success
    # content shall be longer than 40 characters
    assert gdf.expect_column_value_lengths_to_be_between(column="content", min_value=40).success
    # text columns should be type strings
    for column in TEXT_COLUMNS:
        assert gdf.expect_column_values_to_be_of_type(column=column, type_="str")
    # array columns should be type list
    for column in ARRAY_COLUMNS:
        assert gdf.expect_column_values_to_be_of_type(column=column, type_="list")
    # doc_source values should be only ["ds_pwdb","ds_eu_cellar","ds_eu_timeline","ds_ireland_timeline"]
    assert gdf.expect_column_values_to_be_in_set(column="doc_source",
                                                 value_set=["ds_pwdb", "ds_eu_cellar", "ds_eu_timeline",
                                                            "ds_ireland_timeline"]).success
    # date column should have dates in yyyy-mm-dd format
    assert gdf.expect_column_values_to_match_strftime_format(column="date", strftime_format="%Y-%m-%d").success
    # categories values should be only the ones in PWDB
    assert gdf.expect_column_values_to_be_in_set(column="pwdb_category",
                                                 value_set=PWDB_CATEGORIES).success

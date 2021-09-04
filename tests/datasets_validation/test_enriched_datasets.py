import great_expectations as ge
from sem_covid.services.store_registry import store_registry

es_store = store_registry.es_index_store()
ENRICHMENT_COLUMNS = ['businesses', 'citizens', 'workers',
                      'category', 'subcategory', 'type_of_measure', 'funding']
COMMON_COLUMNS = ['title']
DATA_FRAME_INDEX_NAME = ['ds_eu_cellar_enriched', 'ds_eu_timeline_enriched', 'ds_ireland_timeline_enriched']
EU_CELLAR_COLUMNS = ['eurovoc_concepts', 'title', 'content', 'subject_matter_labels']
EU_TIMELINE_COLUMNS = ['title', 'detail_content', 'topics', 'abstract']
IRELAND_TIMELINE_COLUMNS = ['title', 'content', 'page_type', 'keyword']


def validate_enriched_dataset(data_frame_index_name):
    df_from_elastic = es_store.get_dataframe(index_name=data_frame_index_name)
    gdf = ge.from_pandas(df_from_elastic)
    # they contain the enrichment columns
    assert gdf.expect_table_columns_to_match_set(column_set=ENRICHMENT_COLUMNS,
                                                 exact_match=False).success
    # no more than 1% of titles shall be missing
    assert gdf.expect_column_values_to_not_be_null(column="title", mostly=0.99).success
    # no more than 1% of content shall be missing
    assert gdf.expect_column_values_to_not_be_null(column="content", mostly=0.99).success
    # title length shall be greater than 5 chars
    assert gdf.expect_column_value_lengths_to_be_between(column="title", min_value=5).success
    # content shall be longer than 300 characters
    assert gdf.expect_column_value_lengths_to_be_between(column="content", min_value=300).success
    # 'businesses', 'citizens', 'workers' columns are holding binary data (only 1 or 0)
    for column in ENRICHMENT_COLUMNS[:3]:
        assert gdf.expect_column_values_to_be_of_type(column=column, type_="int")
        assert gdf.expect_column_values_to_be_in_set(column=column, value_set=[0, 1]).success
    # 'category', 'subcategory', 'type_of_measure', 'funding' columns should be text
    for column in ENRICHMENT_COLUMNS[3:]:
        assert gdf.expect_column_values_to_be_of_type(column=column, type_="str")
    # enrichment columns should not be empty
    for column in ENRICHMENT_COLUMNS:
        assert gdf.expect_column_values_to_not_be_null(column=column).success
    # title and content columns should not be null and should be text
    for column in COMMON_COLUMNS:
        assert gdf.expect_column_values_to_not_be_null(column=column).success
        assert gdf.expect_column_values_to_be_of_type(column=column, type_="str")
    # 'category', 'subcategory', 'type_of_measure', 'funding' shall have 10 max unique values
    for column in ENRICHMENT_COLUMNS[3:]:
        assert gdf.expect_column_unique_value_count_to_be_between(column=column, max_value=10)


def test_enriched_datasets():
    for index_name in DATA_FRAME_INDEX_NAME:
        validate_enriched_dataset(index_name)


def test_eu_cellar_enriched():
    eu_cellar_df = es_store.get_dataframe(index_name='ds_eu_cellar_enriched')
    gdf = ge.from_pandas(eu_cellar_df)

    for column in EU_CELLAR_COLUMNS:
        assert gdf.expect_column_values_to_not_be_null(column=column).success
        assert gdf.expect_column_values_to_be_of_type(column=column, type_="str")


def test_eu_timeline_enriched():
    eu_timeline_df = es_store.get_dataframe(index_name='ds_eu_timeline_enriched')
    gdf = ge.from_pandas(eu_timeline_df)

    for column in EU_TIMELINE_COLUMNS:
        assert gdf.expect_column_values_to_not_be_null(column=column).success
        assert gdf.expect_column_values_to_be_of_type(column=column, type_="str")


def test_ireland_timeline_enriched():
    ireland_timeline_df = es_store.get_dataframe(index_name='ds_ireland_timeline_enriched')
    gdf = ge.from_pandas(ireland_timeline_df)

    for column in EU_TIMELINE_COLUMNS:
        assert gdf.expect_column_values_to_not_be_null(column=column).success
        assert gdf.expect_column_values_to_be_of_type(column=column, type_="str")




#!/usr/bin/python3

# test_document_similarity_pipelines.py
# Date:  16.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
import pathlib

import numpy as np
import pandas as pd

from sem_covid import config
from sem_covid.services.semantic_similarity_pipelines.document_embedding_pipeline import DocumentEmbeddingPipeline
from sem_covid.services.semantic_similarity_pipelines.document_similarity_pipeline import DocumentSimilarityPipeline, \
    cosine_similarity
from sem_covid.services.semantic_similarity_pipelines.semantic_similarity_sampling_pipeline import \
    SemanticSimilaritySamplingPipeline
from tests.fake_embedding_model_registry import FakeEmbeddingModelRegistry
from tests.fake_store_registry import FakeStoreWithDatasetsRegistry
from tests import TEST_DATA_PATH

TEXTUAL_COLUMNS = ['title', 'background_info_description', 'content_of_measure_description',
                   'use_of_measure_description', 'involvement_of_social_partners_description']

DOCUMENT_EMBEDDINGS_FEATURE_STORE_NAME = 'fs_doc_emb_tfidf'

DOCUMENTS_CONFIGS = {config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME: ['title', 'content'],
                     config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME: ['title', 'abstract', 'detail_content'],
                     config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME: ['title', 'content'],
                     config.PWDB_ELASTIC_SEARCH_INDEX_NAME: TEXTUAL_COLUMNS
                     }

SM_EU_CELLAR_X_PWDB = 'sm_ds_eu_cellar_x_ds_pwdb_tfidfembeddingmodel_cosine_similarity'
METRIC_COLUMN_NAME = 'cosine_similarity'
SAMPLE_INDEX_NAME = 'sm_eu_cellar_x_pwdb_sample_tf_idf_emb_cosine'


def test_fake_store_with_datasets_registry():
    es_store = FakeStoreWithDatasetsRegistry().es_index_store()
    index_names = [config.PWDB_ELASTIC_SEARCH_INDEX_NAME,
                   config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                   config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                   config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME
                   ]
    for index_name in index_names:
        df = es_store.get_dataframe(index_name=index_name)
        assert df is not None
        assert type(df) == pd.DataFrame
        assert len(df) == 100


def test_document_similarity_pipelines():
    store_registry = FakeStoreWithDatasetsRegistry()
    es_store = store_registry.es_index_store()
    embedding_registry = FakeEmbeddingModelRegistry()
    for config_key in DOCUMENTS_CONFIGS.keys():
        df = es_store.get_dataframe(index_name=config_key)
        assert len(df) > 0
        DocumentEmbeddingPipeline(es_index_name=config_key,
                                  textual_columns=DOCUMENTS_CONFIGS[config_key],
                                  embedding_model=embedding_registry.sent2vec_tfidf_avg(),
                                  embedding_model_name='TfIdfEmbeddingModel',
                                  store_registry=store_registry,
                                  doc_emb_feature_store_name=DOCUMENT_EMBEDDINGS_FEATURE_STORE_NAME
                                  ).execute()
    df = es_store.get_dataframe(index_name=DOCUMENT_EMBEDDINGS_FEATURE_STORE_NAME)
    assert len(df) > 0
    DocumentSimilarityPipeline(document_embeddings_index=DOCUMENT_EMBEDDINGS_FEATURE_STORE_NAME,
                               similarity_metric=cosine_similarity,
                               similarity_metric_name=METRIC_COLUMN_NAME,
                               store_registry=store_registry
                               ).execute()
    sm_df = es_store.get_dataframe(index_name=SM_EU_CELLAR_X_PWDB)
    assert len(sm_df) > 0
    assert METRIC_COLUMN_NAME in sm_df.columns
    SemanticSimilaritySamplingPipeline(semantic_similarity_index_name=SM_EU_CELLAR_X_PWDB,
                                       doc_emb_feature_store_name=DOCUMENT_EMBEDDINGS_FEATURE_STORE_NAME,
                                       sample_index_name=SAMPLE_INDEX_NAME,
                                       sample_size=10,
                                       metric_column_name=METRIC_COLUMN_NAME,
                                       store_registry=store_registry
                                       ).execute()
    sample_df = es_store.get_dataframe(index_name=SAMPLE_INDEX_NAME)
    assert len(sample_df) == 10

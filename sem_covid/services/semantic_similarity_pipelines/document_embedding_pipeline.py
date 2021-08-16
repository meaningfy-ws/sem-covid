#!/usr/bin/python3

# document_embedding_pipeline.py
# Date:  26.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
import re

import pandas as pd

from sem_covid.adapters.abstract_model import SentenceEmbeddingModelABC
from sem_covid.services.store_registry import StoreRegistryABC

DOCUMENT_TEXT = 'text'
DOCUMENT_SEGMENT = 'segment_type'
DOCUMENT_SEGMENT_ID = 'segment_id'
DOCUMENT_SOURCE = 'source'
DOCUMENT_PREPARE_METHOD = 'prepare_method'
DOCUMENT_EMBEDDING = 'embedding'
DOCUMENT_EMBEDDING_METHOD = 'embedding_method'
DOCUMENT_TEXTUAL_COLUMNS = 'textual_columns'


class DocumentEmbeddingPipeline:
    """
        This pipeline aims to calculate embedding vectors for documents, this process is done in 4 steps:
        1. Downloading documents.
        2. Textual data processing.
        3. Transforming documents into embedding vectors.
        4. Storage of calculated embedding vectors.
    """
    def __init__(self, es_index_name: str, textual_columns: list,
                 embedding_model: SentenceEmbeddingModelABC, embedding_model_name: str,
                 store_registry: StoreRegistryABC, doc_emb_feature_store_name: str,
                 text_limit_chars: int = 5000):
        """
            Document embedding pipeline depends on the following parameters:
        :param es_index_name: elastic search index name for concrete dataset
        :param textual_columns: textual columns names from concrete dataset
        :param embedding_model: embedding model that will be used to calculate embedding documents
        :param embedding_model_name: model embedding name to be stored in metadata
        :param store_registry: register of different types of storage
        :param doc_emb_feature_store_name: the name of the feature store for the calculated embedding
        :param text_limit_chars: the limit of characters that will be processed from the textual data of the dataset
        """
        self.es_index_name = es_index_name
        self.textual_columns = textual_columns
        self.prepared_dataset = None
        self.dataset = None
        self.model = embedding_model
        self.model_name = embedding_model_name
        self.text_limit_chars = text_limit_chars
        self.store_registry = store_registry
        self.doc_emb_feature_store_name = doc_emb_feature_store_name

    def load_documents(self):
        """
            This method performs the step of loading the required documents from the preconfigured dateset.
        :return:
        """
        es_index_store = self.store_registry.es_index_store()
        self.dataset = es_index_store.get_dataframe(self.es_index_name)

    def prepare_textual_columns(self):
        """
            This method prepares the textual data before calculating embeddings based on them.
        :return:
        """
        assert self.dataset is not None
        self.dataset.dropna(subset=self.textual_columns, inplace=True)
        for textual_column in self.textual_columns:
            self.dataset[textual_column] = self.dataset[textual_column].apply(
                lambda x: re.sub("[\s\t\r\n]+", " ", x) if x else x)
        self.dataset[DOCUMENT_TEXT] = self.dataset[self.textual_columns].agg(lambda texts:
                                                                             ". ".join(texts)[:self.text_limit_chars],
                                                                             axis=1)
        self.prepared_dataset = pd.DataFrame(self.dataset[DOCUMENT_TEXT])
        self.prepared_dataset[DOCUMENT_SOURCE] = self.es_index_name
        self.prepared_dataset[DOCUMENT_SEGMENT] = 'document'
        self.prepared_dataset[DOCUMENT_SEGMENT_ID] = 0
        self.prepared_dataset[DOCUMENT_PREPARE_METHOD] = 'join_textual_columns'
        self.prepared_dataset[DOCUMENT_TEXTUAL_COLUMNS] = [self.textual_columns] * len(self.prepared_dataset)

    def compute_embeddings(self):
        """
           This method performs the step of calculating embedding based on the textual data in the dataset.
        :return:
        """
        assert self.model is not None
        assert self.prepared_dataset is not None
        self.prepared_dataset[DOCUMENT_EMBEDDING] = self.model.encode(
            self.prepared_dataset[DOCUMENT_TEXT].tolist())
        self.prepared_dataset[DOCUMENT_EMBEDDING_METHOD] = self.model_name

    def store_embeddings(self):
        """
            This method performs the storage step of the calculated embedding
        :return:
        """
        assert self.prepared_dataset is not None
        assert DOCUMENT_EMBEDDING in self.prepared_dataset.columns
        es_feature_store = self.store_registry.es_feature_store()
        es_feature_store.put_features(features_name=self.doc_emb_feature_store_name,
                                      content=self.prepared_dataset)

    def execute(self):
        """
           This method performs the steps of the pipeline in the required order.
        :return:
        """
        self.load_documents()
        self.prepare_textual_columns()
        self.compute_embeddings()
        self.store_embeddings()

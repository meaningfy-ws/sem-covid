#!/usr/bin/python3

# semantic_similarity_sampling_pipeline.py
# Date:  16.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
import math
from sem_covid.services.store_registry import store_registry


class SemanticSimilaritySamplingPipeline:
    """
        This class performs a sampling pipeline of a list of semantic similarities between documents.
    """
    def __init__(self, semantic_similarity_index_name: str,
                 doc_emb_feature_store_name: str,
                 sample_index_name: str,
                 sample_size: int,
                 metric_column_name: str
                 ):
        """
            This pipeline depends on the following parameters:
        :param semantic_similarity_index_name: elastic search index name where the similarity list was stored
        :param doc_emb_feature_store_name: feature store with document embeddings
        :param sample_index_name: new elastic search index name for sample
        :param sample_size: number of document pairs what will be contained in sample
        :param metric_column_name: column name where is stored semantic similarity metric
        """
        self.semantic_similarity_index_name = semantic_similarity_index_name
        self.doc_emb_feature_store_name = doc_emb_feature_store_name
        self.metric_column_name = metric_column_name
        self.sample_index_name = sample_index_name
        self.sample_size = sample_size
        self.sm_df = None
        self.sm_sample = None
        self.doc_emb_df = None

    def load_data(self):
        """
            This method loads the required data.
        :return:
        """
        es_store = store_registry.es_index_store()
        self.sm_df = es_store.get_dataframe(index_name=self.semantic_similarity_index_name)
        self.doc_emb_df = es_store.get_dataframe(index_name=self.doc_emb_feature_store_name)

    def compute_sampling(self):
        """
            This method performs the sampling operation.
        :return:
        """
        self.sm_df.sort_values(by=self.metric_column_name, inplace=True)
        step = math.floor(len(self.sm_df) / self.sample_size)
        self.sm_sample = self.sm_df.iloc[:self.sample_size * step:step]
        self.sm_sample['text_left'] = self.sm_sample.apply(lambda df_row: self.doc_emb_df.loc[df_row[0], 'text'],
                                                           axis=1)
        self.sm_sample['text_right'] = self.sm_sample.apply(lambda df_row: self.doc_emb_df.loc[df_row[1], 'text'],
                                                            axis=1)

    def store_sample(self):
        """
            This method stores the calculated sample.
        :return:
        """
        es_store = store_registry.es_index_store()
        es_store.put_dataframe(index_name=self.sample_index_name, content=self.sm_sample)

    def execute(self):
        """
            This method performs the steps of the pipeline in the required order.
        :return:
        """
        self.load_data()
        self.compute_sampling()
        self.store_sample()

#!/usr/bin/python3

# ireland_enrich_pipeline.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to configure the enrichment pipeline for the Ireland-Timeline dataset.
"""

import numpy as np
import pandas as pd

from sem_covid import config
from sem_covid.services.enrich_pipelines.base_enrich_pipeline import BaseEnrichPipeline, BasePrepareDatasetPipeline, \
    EMBEDDING_COLUMN
from sem_covid.services.sc_wrangling.mean_vectorizer import text_to_vector

IRELAND_TIMELINE_TEXT_COLUMNS = ['title', 'content', 'keyword']


class IrelandTimeLinePreparePipeline(BasePrepareDatasetPipeline):
    """
        This class is intended to perform specialized steps
         for the Ireland-Timeline dataset.
    """
    def __init__(self):
        """
            Pipeline initialization with required configurations.
        """
        features_name = 'fs_ireland_timeline'
        super().__init__(ds_es_index=config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME,
                         features_store_name=features_name)

    def prepare_textual_columns(self):
        """
            Preparation of textual data.
        :return:
        """
        text_df = pd.DataFrame(self.dataset[IRELAND_TIMELINE_TEXT_COLUMNS])
        text_df.replace(np.nan, '', regex=True, inplace=True)
        text_df[EMBEDDING_COLUMN] = text_df.agg(' '.join, axis=1)
        text_df.reset_index(drop=True, inplace=True)
        self.dataset = text_df

    def create_embeddings(self):
        """
            Creating embeddings vectors.
        :return:
        """
        self.dataset[EMBEDDING_COLUMN] = self.dataset[EMBEDDING_COLUMN].apply(
            lambda x: text_to_vector(x, self.l2v_dict))


class IrelandTimeLineEnrich:
    """
        This class aims to combine the pipeline of data preparation
         and enrichment of the Ireland-Timeline dataset.
    """
    @classmethod
    def prepare_dataset(cls):
        """
            Method for making preparation pipeline.
        :return:
        """
        worker = IrelandTimeLinePreparePipeline()
        worker.execute()

    @classmethod
    def enrich_dataset(cls):
        """
             Method for making enrich pipeline.
        :return:
        """
        worker = BaseEnrichPipeline(feature_store_name='fs_ireland_timeline',
                                    ds_es_index=config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME
                                    )
        worker.execute()
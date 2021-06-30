import numpy as np
import pandas as pd

from sem_covid import config
from sem_covid.services.enrich_pipelines.base_enrich_pipeline import BaseEnrichPipeline, BasePrepareDatasetPipeline, \
    EMBEDDING_COLUMN
from sem_covid.services.sc_wrangling.mean_vectorizer import text_to_vector

EU_CELLAR_TEXT_COLUMNS = ['title']


class EuCellarPreparePipeline(BasePrepareDatasetPipeline):

    def __init__(self):
        features_name = 'fs_eu_cellar'
        super().__init__(ds_es_index=config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME, features_store_name=features_name)

    def prepare_textual_columns(self):
        text_df = pd.DataFrame(self.dataset[EU_CELLAR_TEXT_COLUMNS])
        text_df.replace(np.nan, '', regex=True, inplace=True)
        text_df[EMBEDDING_COLUMN] = text_df.agg(' '.join, axis=1)
        text_df.reset_index(drop=True, inplace=True)
        self.dataset = text_df

    def create_embeddings(self):
        self.dataset[EMBEDDING_COLUMN] = self.dataset[EMBEDDING_COLUMN].apply(
            lambda x: text_to_vector(x, self.l2v_dict))


class EuCellarEnrich:

    @classmethod
    def prepare_dataset(cls):
        worker = EuCellarPreparePipeline()
        worker.execute()

    @classmethod
    def enrich_dataset(cls):
        worker = BaseEnrichPipeline(feature_store_name='fs_eu_cellar',
                                    ds_es_index=config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                                    )
        worker.execute()

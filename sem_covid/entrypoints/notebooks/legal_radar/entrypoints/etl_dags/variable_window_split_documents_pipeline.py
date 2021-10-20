#!/usr/bin/python3

# variable_window_split_documents_pipeline.py
# Date:  20.10.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
from sem_covid import config
from sem_covid.adapters.dag.abstract_dag_pipeline import DagPipeline
from sem_covid.entrypoints.notebooks.legal_radar.services.split_documents_pipeline import WindowedSplitDocumentsPipeline
from sem_covid.services.model_registry import EmbeddingModelRegistry
from sem_covid.services.store_registry import store_registry

TEXTUAL_COLUMNS = ['title', 'content']
FIN_REG_SPLITTED_ES_INDEX = 'ds_finreg_splitted'

EXPERIMENT_CONFIGS = [
    #(1, 1),
    (2, 1),
    (5, 2),
    (10, 5),
    (20, 10),
    (50, 25),
    (100, 50)
]


class VariableWindowSplitPipeline(DagPipeline):

    def windowed_split(self):
        for split_window_size, split_window_step in EXPERIMENT_CONFIGS:
            result_es_index_name = '_'.join(map(str, (FIN_REG_SPLITTED_ES_INDEX, split_window_size, split_window_step)))
            print(f'Start document splitter for: {result_es_index_name}')
            windowed_split_documents_pipeline = WindowedSplitDocumentsPipeline(
                dataset_es_index_name=config.EU_FINREG_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                result_es_index_name=result_es_index_name,
                textual_columns=TEXTUAL_COLUMNS,
                split_window_size=split_window_size,
                split_window_step=split_window_step,
                store_registry=store_registry,
                embedding_model_registry=EmbeddingModelRegistry())
            windowed_split_documents_pipeline.execute()

    def get_steps(self) -> list:
        return [self.windowed_split]

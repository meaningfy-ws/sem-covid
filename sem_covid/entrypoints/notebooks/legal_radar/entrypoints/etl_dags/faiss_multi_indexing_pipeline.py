#!/usr/bin/python3

# faiss_multi_indexing_pipeline.py
# Date:  20.10.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
from sem_covid.adapters.dag.abstract_dag_pipeline import DagPipeline
from sem_covid.entrypoints.notebooks.legal_radar.services.faiss_indexing_pipeline import FaissIndexingPipeline
from sem_covid.entrypoints.notebooks.legal_radar.services.split_documents_pipeline import TEXT_PIECE_EMBEDDING
from sem_covid.services.store_registry import store_registry

FAISS_BUCKET_NAME = 'faiss-index'
FAISS_INDEX_FINREG_NAME = 'faiss_index_finreg'
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


class FAISSMultipleIndexingPipeline(DagPipeline):

    def create_index(self):
        for split_window_size, split_window_step in EXPERIMENT_CONFIGS:
            fin_reg_es_index_name = '_'.join(
                map(str, (FIN_REG_SPLITTED_ES_INDEX, split_window_size, split_window_step)))
            faiss_index_finreg_name = '_'.join(
                map(str, (FAISS_INDEX_FINREG_NAME, split_window_size, split_window_step, '.pkl')))
            print(fin_reg_es_index_name, faiss_index_finreg_name)
            faiss_indexing_pipeline = FaissIndexingPipeline(es_index_name=fin_reg_es_index_name,
                                                            embedding_column_name=TEXT_PIECE_EMBEDDING,
                                                            result_bucket_name=FAISS_BUCKET_NAME,
                                                            result_faiss_index_name=faiss_index_finreg_name,
                                                            store_registry=store_registry)
            faiss_indexing_pipeline.execute()

    def get_steps(self) -> list:
        return [self.create_index]

#!/usr/bin/python3

# document_similarity_pipeline.py
# Date:  27.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
import concurrent.futures
import hashlib

import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import pairwise_distances
import seaborn as sns
from pathlib import Path
from sem_covid.services.semantic_similarity_pipelines.document_embedding_pipeline import DOCUMENT_EMBEDDING, \
    DOCUMENT_EMBEDDING_METHOD
from sem_covid.services.store_registry import StoreRegistryABC

DOCUMENT_NAME_X = 'name_x'
DOCUMENT_NAME_Y = 'name_y'
SIMILARITY_MATRIX = 'similarity_matrix'
SIMILARITY_LIST = 'similarity_list'
DOCUMENT_ID = 'document_id'
SIMILARITY_METRIC = 'similarity_metric'
SIMILARITY_METRIC_VALUE = 'similarity_metric_value'
DOCUMENT_EMBEDDING_METHOD_NOT_FOUND = 'not_found_embedding_method'


class DocumentSimilarityPipeline:

    def __init__(self, document_embeddings_index: str, similarity_metric,
                 similarity_metric_name: str,
                 store_registry: StoreRegistryABC,
                 figures_path: Path = None
                 ):
        self.document_embeddings_index = document_embeddings_index
        self.similarity_metric = similarity_metric
        self.prepared_data = None
        self.document_embeddings = {}
        self.dataset_names = []
        self.figures_path = figures_path
        self.store_registry = store_registry
        self.similarity_metric_name = similarity_metric_name
        self.document_embeddings_method = DOCUMENT_EMBEDDING_METHOD_NOT_FOUND
        self.dataset = pd.DataFrame()

    def load_document_embeddings(self):
        es_index_store = self.store_registry.es_index_store()
        self.dataset = es_index_store.get_dataframe(index_name=self.document_embeddings_index)
        self.dataset_names = list(set(self.dataset.source.values))
        self.document_embeddings = {dataset_name: self.dataset[self.dataset.source == dataset_name]
                                    for dataset_name in self.dataset_names}

    def prepare_similarity_data(self):
        def prepare_worker(name_x: str, name_y: str) -> dict:
            similarity_matrix = pd.DataFrame(
                pairwise_distances(X=self.document_embeddings[name_x][DOCUMENT_EMBEDDING].to_list(),
                                   Y=self.document_embeddings[name_y][DOCUMENT_EMBEDDING].to_list(),
                                   metric=self.similarity_metric),
                columns=self.document_embeddings[name_y].index.to_list(),
                index=self.document_embeddings[name_x].index.to_list()
            )
            similarity_matrix = similarity_matrix.stack()
            indexes = similarity_matrix.index.to_flat_index()
            values = similarity_matrix.values
            similarity_list = pd.DataFrame([indexes[index] + (values[index],) for index in range(0, len(values))],
                                           columns=[name_x, name_y, self.similarity_metric_name]
                                           )
            del similarity_matrix
            return {DOCUMENT_NAME_X: name_x, DOCUMENT_NAME_Y: name_y,
                    SIMILARITY_LIST: similarity_list}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(prepare_worker, name_x, name_y)
                       for name_x in self.dataset_names
                       for name_y in self.dataset_names[self.dataset_names.index(name_x):]]
            self.prepared_data = [future.result() for future in futures]

    def save_similarity_list(self):
        es_feature_store = self.store_registry.es_feature_store()
        self.document_embeddings_method = list(self.document_embeddings.values())[0][DOCUMENT_EMBEDDING_METHOD][0]
        for data in self.prepared_data:
            similarity_documents_name = f"{data[DOCUMENT_NAME_X]}_x_{data[DOCUMENT_NAME_Y]}"
            similarity_feature_name = "_".join(["sm",
                                                similarity_documents_name,
                                                self.document_embeddings_method,
                                                self.similarity_metric_name]
                                               ).lower()
            es_feature_store.put_features(features_name=similarity_feature_name,
                                          content=data[SIMILARITY_LIST]
                                          )

    # def save_similarity_pairs(self):
    #
    #     def generate_new_row(row_index, dataframe, column_suffix):
    #         new_row = pd.Series(dataframe.loc[row_index])
    #         new_row[DOCUMENT_ID] = new_row.name
    #         new_row.index = list(map(lambda x: x + column_suffix, new_row.index))
    #         return new_row
    #
    #     def combine_two_rows(left_row: pd.Series, right_row: pd.Series, similarity_metric: str,
    #                          similarity_metric_value: float) -> pd.Series:
    #         new_combined_row = left_row.append(right_row)
    #         new_combined_row[SIMILARITY_METRIC] = similarity_metric
    #         new_combined_row[SIMILARITY_METRIC_VALUE] = similarity_metric_value
    #         new_combined_row.name = hashlib.sha256(
    #             (str(left_row.name) + str(right_row.name)).encode('utf-8')).hexdigest()
    #         return new_combined_row
    #
    #     es_index_store = self.store_registry.es_index_store()
    #
    #     for data in self.prepared_data:
    #         sim_matrix = data[SIMILARITY_MATRIX]
    #         sim_pairs_list = [combine_two_rows(generate_new_row(row_index_left, self.dataset, '_left'),
    #                                            generate_new_row(row_index_right, self.dataset, '_right'),
    #                                            self.similarity_metric_name,
    #                                            sim_matrix.loc[row_index_left][row_index_right])
    #                           for row_index_left in sim_matrix.index
    #                           for row_index_right in sim_matrix.columns]
    #         similarity_pairs_df = pd.DataFrame(sim_pairs_list)
    #         es_index_store.put_dataframe(index_name=f"sm_{data[DOCUMENT_NAME_X]}_X_{data[DOCUMENT_NAME_Y]}",
    #                                      content=similarity_pairs_df)

    def plot_histograms(self):
        if self.figures_path:
            plt.subplots(figsize=(10, 5))
            for data in self.prepared_data:
                plot_title = f"sm_{data[DOCUMENT_NAME_X]}_X_{data[DOCUMENT_NAME_Y]}_{self.document_embeddings_method}"
                plot = sns.histplot(data=data[SIMILARITY_LIST]).set_title(plot_title)
                plot.figure.savefig(self.figures_path / (plot_title + '.png'))
                plot.figure.clf()

    def execute(self):
        self.load_document_embeddings()
        self.prepare_similarity_data()
        self.save_similarity_list()
        # self.save_similarity_pairs()
        self.plot_histograms()

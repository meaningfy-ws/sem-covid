#!/usr/bin/python3

# document_similarity_pipeline.py
# Date:  27.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
import concurrent.futures
import hashlib

import numpy as np
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


def cosine_similarity(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

class DocumentSimilarityPipeline:
    """
            This pipeline performs the document similarity calculation based on document embeddings.
        This pipeline consists of the following steps:
        1. Download document embeddings.
        2. Calculation of similarity data.
        3. Saving similarities.
        4. [Optional] Drawing histograms based on the similarity distribution between datasets.

    """

    def __init__(self, document_embeddings_index: str, similarity_metric,
                 similarity_metric_name: str,
                 store_registry: StoreRegistryABC,
                 figures_path: Path = None
                 ):
        """
           Document similarity pipeline  depends on the following parameters.
        :param document_embeddings_index: elastic search index name where is stored document embeddings for all datasets
        :param similarity_metric: function or metric name of similarity
        :param similarity_metric_name: similarity metric name what will be stored in metadata.
        :param store_registry: a register of different types of storage
        :param figures_path: path where histogram figures will be stored
        """
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
        """
           This method performs the step of loading document embeddings.
        :return:
        """
        es_index_store = self.store_registry.es_index_store()
        self.dataset = es_index_store.get_dataframe(index_name=self.document_embeddings_index)
        self.dataset_names = list(set(self.dataset.source.values))
        self.document_embeddings = {dataset_name: self.dataset[self.dataset.source == dataset_name]
                                    for dataset_name in self.dataset_names}

    def prepare_similarity_data(self):
        """
            This method calculates the similarity between documents based on document embeddings.
        :return:
        """

        def prepare_worker(name_x: str, name_y: str) -> dict:
            """
                This function is a nested auxiliary function in order to perform a task in parallel.
            :param name_x: the name of the dataset that will be placed on the X axis in the similarity matrix.
            :param name_y: the name of the dataset that will be placed on the Y axis in the similarity matrix.
            :return:
            """
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
        """
            This method saves the calculated similarities in a list of tuples, stored in DataFrame formats.
        :return:
        """
        es_index_store = self.store_registry.es_index_store()
        self.document_embeddings_method = list(self.document_embeddings.values())[0][DOCUMENT_EMBEDDING_METHOD][0]
        for data in self.prepared_data:
            similarity_documents_name = f"{data[DOCUMENT_NAME_X]}_x_{data[DOCUMENT_NAME_Y]}"
            similarity_feature_name = "_".join(["sm",
                                                similarity_documents_name,
                                                self.document_embeddings_method,
                                                self.similarity_metric_name]
                                               ).lower()
            es_index_store.put_dataframe(index_name=similarity_feature_name,
                                         content=data[SIMILARITY_LIST]
                                         )

    def plot_histograms(self):
        """
            This method generates histograms based on the similarity distribution between the documents of two datasets.
        :return:
        """
        if self.figures_path:
            plt.subplots(figsize=(10, 5))
            for data in self.prepared_data:
                plot_title = f"sm_{data[DOCUMENT_NAME_X]}_X_{data[DOCUMENT_NAME_Y]}_{self.document_embeddings_method}"
                plot = sns.histplot(data=data[SIMILARITY_LIST]).set_title(plot_title)
                plot.figure.savefig(self.figures_path / (plot_title + '.png'))
                plot.figure.clf()

    def execute(self):
        """
            This method performs the steps of the pipeline in the required order.
        :return:
        """
        self.load_document_embeddings()
        self.prepare_similarity_data()
        self.save_similarity_list()
        self.plot_histograms()

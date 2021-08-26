#!/usr/bin/python3

# faiss_indexing_pipeline.py
# Date:  25.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import pickle
import numpy as np
import faiss

from sem_covid.services.store_registry import store_registry, StoreRegistryABC


class FaissIndexingPipeline:

    def __init__(self, es_index_name: str,
                 embedding_column_name: str,
                 result_bucket_name: str,
                 result_faiss_index_name: str,
                 store_registry: StoreRegistryABC):
        self.es_index_name = es_index_name
        self.store_registry = store_registry
        self.embedding_column_name = embedding_column_name
        self.result_bucket_name = result_bucket_name
        self.result_faiss_index_name = result_faiss_index_name
        self.dataset = None
        self.embeddings = None
        self.faiss_index = None

    def load_dataset(self):
        es_store = self.store_registry.es_index_store()
        self.dataset = es_store.get_dataframe(index_name=self.es_index_name)

    def prepare_embeddings(self):
        self.embeddings = self.dataset[self.embedding_column_name].values
        self.embeddings = np.array([np.array(embedding).astype('float32')
                                    for embedding in self.embeddings]).astype("float32")

    def embeddings_indexing(self):
        self.faiss_index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.faiss_index = faiss.IndexIDMap(self.faiss_index)
        self.faiss_index.add_with_ids(self.embeddings, np.array(range(0, len(self.dataset.index.values))))

    def store_faiss_index(self):
        minio_store = store_registry.minio_object_store(self.result_bucket_name)
        minio_store.put_object(object_name=self.result_faiss_index_name,
                               content=pickle.dumps(faiss.serialize_index(self.faiss_index))
                               )

    def execute(self):
        self.load_dataset()
        self.prepare_embeddings()
        self.embeddings_indexing()
        self.store_faiss_index()

#!/usr/bin/python3

# test_document_embedding_model.py
# Date:  08.09.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
from sem_covid import config
from sem_covid.adapters.embedding_models import TfIdfDocumentEmbeddingModel, BasicSentenceSplitterModel
from sem_covid.services.model_registry import UniversalSentenceEmbeddingModel
from tests.fake_store_registry import FakeStoreWithDatasetsRegistry


def test_tfidf_document_embedding_model():
    doc_emb_model = TfIdfDocumentEmbeddingModel(sent_emb_model=UniversalSentenceEmbeddingModel(),
                                                sent_splitter=BasicSentenceSplitterModel(),
                                                top_k=10)
    store_registry = FakeStoreWithDatasetsRegistry()
    es_store = store_registry.es_index_store()
    dataset = es_store.get_dataframe(index_name=config.PWDB_ELASTIC_SEARCH_INDEX_NAME)
    documents = dataset['content_of_measure_description'].values
    doc_emb = doc_emb_model.encode(documents)
    assert len(doc_emb) == len(documents)


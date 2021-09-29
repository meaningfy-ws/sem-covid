from tests.fake_store_registry import FakeStoreWithDatasetsRegistry
from sem_covid import config
from transformers import AutoTokenizer, AutoModel
from sem_covid.services.topic_modeling_pipelines.doc_embedding_pipeline import DocEmbeddingPipeline


def test_doc_embedding_pipeline():
    store_registry = FakeStoreWithDatasetsRegistry()
    es_store = store_registry.es_index_store()

    df = es_store.get_dataframe(index_name=config.UNIFIED_DATASET_ELASTIC_SEARCH_INDEX_NAME)
    assert len(df) > 0

    bert_base_uncased_eurlex_tokenizer = AutoTokenizer.from_pretrained('nlpaueb/bert-base-uncased-eurlex')
    bert_base_uncased_eurlex_model = AutoModel.from_pretrained('nlpaueb/bert-base-uncased-eurlex',
                                                               output_hidden_states=True)

    DocEmbeddingPipeline(store_registry=store_registry,
                         es_index_name=config.UNIFIED_DATASET_ELASTIC_SEARCH_INDEX_NAME,
                         textual_columns=['title', 'content'],
                         tokenizer=bert_base_uncased_eurlex_tokenizer,
                         embedding_model=bert_base_uncased_eurlex_model,
                         doc_emb_feature_store_name='fs_doc_embeddings_for_topic_modeling').execute()

    df = es_store.get_dataframe(index_name='fs_doc_embeddings_for_topic_modeling')
    assert len(df) > 0

#!/usr/bin/python3

# fake_embedding_model_registry.py
# Date:  17.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
from sem_covid.adapters.abstract_model import SentenceEmbeddingModelABC, WordEmbeddingModelABC
from sem_covid.adapters.embedding_models import Word2VecEmbeddingModel, AverageSentenceEmbeddingModel, \
    BasicTokenizerModel
from sem_covid.services.model_registry import EmbeddingModelRegistryABC
from tests.fake_keyed_vectors import FakeKeyedVectors


class FakeEmbeddingModelRegistry(EmbeddingModelRegistryABC):

    def word2vec_law(self) -> WordEmbeddingModelABC:
        word2vec = FakeKeyedVectors(vector_size=200)
        word2vec_emb_model = Word2VecEmbeddingModel(word2vec=word2vec)
        return word2vec_emb_model

    def sent2vec_avg(self) -> SentenceEmbeddingModelABC:
        return AverageSentenceEmbeddingModel(
            word_embedding_model=self.word2vec_law(),
            tokenizer=BasicTokenizerModel()
        )

    def sent2vec_tfidf_avg(self) -> SentenceEmbeddingModelABC:
        return AverageSentenceEmbeddingModel(
            word_embedding_model=self.word2vec_law(),
            tokenizer=BasicTokenizerModel()
        )

    def sent2vec_universal_sent_encoding(self) -> SentenceEmbeddingModelABC:
        return AverageSentenceEmbeddingModel(
            word_embedding_model=self.word2vec_law(),
            tokenizer=BasicTokenizerModel()
        )

    def sent2vec_eurlex_bert(self) -> SentenceEmbeddingModelABC:
        return AverageSentenceEmbeddingModel(
            word_embedding_model=self.word2vec_law(),
            tokenizer=BasicTokenizerModel()
        )

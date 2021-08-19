#!/usr/bin/python3

# test_word_embedding_model.py
# Date:  21.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from sem_covid.adapters.abstract_model import WordEmbeddingModelABC
from sem_covid.adapters.embedding_models import Word2VecEmbeddingModel
from tests.fake_keyed_vectors import FakeKeyedVectors


def test_word2vec_embedding_model():
    word2vec = FakeKeyedVectors(vector_size=200)
    assert word2vec is not None
    assert word2vec.vector_size == 200
    word2vec_emb_model = Word2VecEmbeddingModel(word2vec=word2vec)
    assert isinstance(word2vec_emb_model, WordEmbeddingModelABC)
    tokens = ['hello', 'this', 'hello', 'is', 'a', 'test']
    embeddings = word2vec_emb_model.encode(tokens=tokens)
    assert len(embeddings) == len(tokens)
    assert embeddings[0] == embeddings[2]
    assert embeddings[0] != embeddings[1]

#!/usr/bin/python3

# test_sentence_embedding_model.py
# Date:  21.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from sem_covid.adapters.abstract_model import SentenceEmbeddingModelABC, WordEmbeddingModelABC
from sem_covid.adapters.embedding_models import (AverageSentenceEmbeddingModel, Word2VecEmbeddingModel,
                                                 BasicTokenizerModel, SpacyTokenizerModel, TfIdfSentenceEmbeddingModel,
                                                 UniversalSentenceEmbeddingModel,
                                                 EurLexBertSentenceEmbeddingModel)
from tests.unit.conftest import nlp
from tests.fake_keyed_vectors import FakeKeyedVectors

SENTENCES = [
    'Rather than having all of its functionality built into its core.',
    'Python was designed to be highly extensible (with modules).',
    'Rather than having all of its functionality built into its core.',
    'This compact modularity has made it particularly popular as a means of adding programmable interfaces to existing applications.',
    "Van Rossum's vision of a small core language with a large standard library and easily extensible interpreter stemmed from his frustrations with ABC, which espoused the opposite approach."
]


def check_sentence_embedding_model(sentence_embedding_model: SentenceEmbeddingModelABC):
    assert sentence_embedding_model is not None
    assert isinstance(sentence_embedding_model, SentenceEmbeddingModelABC)
    embeddings = sentence_embedding_model.encode(sentences=SENTENCES)
    assert embeddings is not None
    assert len(embeddings) == len(SENTENCES)
    assert embeddings[0] != embeddings[1]
    assert embeddings[0] == embeddings[2]


def get_word2vec_emb_model() -> WordEmbeddingModelABC:
    word2vec = FakeKeyedVectors(vector_size=200)
    assert word2vec is not None
    assert word2vec.vector_size == 200
    word2vec_emb_model = Word2VecEmbeddingModel(word2vec=word2vec)
    assert isinstance(word2vec_emb_model, WordEmbeddingModelABC)
    return word2vec_emb_model


def test_average_sentence_embedding_model():
    avg_sentence_embedding_model_basic = AverageSentenceEmbeddingModel(
        word_embedding_model=get_word2vec_emb_model(),
        tokenizer=BasicTokenizerModel()
    )
    check_sentence_embedding_model(avg_sentence_embedding_model_basic)
    avg_sentence_embedding_model_spacy = AverageSentenceEmbeddingModel(
        word_embedding_model=get_word2vec_emb_model(),
        tokenizer=SpacyTokenizerModel(spacy_tokenizer=nlp)
    )
    check_sentence_embedding_model(avg_sentence_embedding_model_spacy)


def test_tf_idf_sentence_embedding_model():
    tf_idf_sentence_embedding_model_basic = TfIdfSentenceEmbeddingModel(
        word_embedding_model=get_word2vec_emb_model(),
        tokenizer=BasicTokenizerModel()
    )
    check_sentence_embedding_model(tf_idf_sentence_embedding_model_basic)
    tf_idf_sentence_embedding_model_spacy = TfIdfSentenceEmbeddingModel(
        word_embedding_model=get_word2vec_emb_model(),
        tokenizer=SpacyTokenizerModel(spacy_tokenizer=nlp)
    )
    check_sentence_embedding_model(tf_idf_sentence_embedding_model_spacy)


def test_universal_sentence_embedding_model():
    universal_sentence_embedding_model = UniversalSentenceEmbeddingModel()
    check_sentence_embedding_model(universal_sentence_embedding_model)


def test_eur_lex_bert_sentence_embedding_model():
    eur_lex_bert_sentence_embedding_model = EurLexBertSentenceEmbeddingModel()
    check_sentence_embedding_model(eur_lex_bert_sentence_embedding_model)

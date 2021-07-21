# -*- coding: utf-8 -*-
# Date    : 20.07.2021 
# Author  : Stratulat Ștefan
# File    : embedding_models.py
# Software: PyCharm
from typing import List

import numpy as np
from gensim.models import KeyedVectors

from sem_covid.adapters.abstract_model import (WordEmbeddingModelABC, SentenceEmbeddingModelABC,
                                               TokenizerModelABC)
import tensorflow_hub as hub

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from transformers import AutoTokenizer, AutoModel, BertModel, BertTokenizerFast


class BasicTokenizerModel(TokenizerModelABC):

    def tokenize(self, text: str) -> List[str]:
        return text.split(' ')


class SpacyTokenizerModel(TokenizerModelABC):

    def __init__(self, spacy_nlp):
        self._spacy_nlp = spacy_nlp

    def tokenize(self, text: str) -> List[str]:
        return list(map(str, self._spacy_nlp(text)))


class Word2VecEmbeddingModel(WordEmbeddingModelABC):

    def __init__(self, word2vec: KeyedVectors):
        self._word2vec = word2vec
        self._vector_dimension = word2vec.vector_size

    def encode(self, tokens: List[str]) -> List:
        return [self._word2vec[word].tolist() if word in self._word2vec else np.zeros(self._vector_dimension).tolist()
                for word in tokens]


class AverageSentenceEmbeddingModel(SentenceEmbeddingModelABC):

    def __init__(self, word_embedding_model: WordEmbeddingModelABC, tokenizer: TokenizerModelABC):
        self._word_embedding_model = word_embedding_model
        self._tokenizer = tokenizer

    def encode(self, sentences: List[str]) -> List:
        results = []
        for sentence in sentences:
            embeddings = self._word_embedding_model.encode(self._tokenizer.tokenize(sentence))
            results += [np.mean([np.zeros(len(embeddings[0])).tolist()] + embeddings, axis=0).tolist()]
        return results


class TfIdfSentenceEmbeddingModel(AverageSentenceEmbeddingModel):

    def encode_one_sentence(self, sentence: str, tf_idf_row: pd.Series):
        tokens = self._tokenizer.tokenize(sentence)
        embeddings = self._word_embedding_model.encode(tokens)
        sum_weights = 0
        results = []
        for index in range(0, len(tokens)):
            if tokens[index] in tf_idf_row.index:
                weight = tf_idf_row[tokens[index]]
                sum_weights += weight
                results += [(weight * np.array(embeddings[index])).tolist()]

        return (np.sum(results, axis=0) / sum_weights).tolist()

    def encode(self, sentences: List[str]) -> List:
        tf_idf_vectors = TfidfVectorizer()
        tf_idf_matrix = pd.DataFrame(tf_idf_vectors.fit_transform(sentences).todense().tolist(),
                                     columns=tf_idf_vectors.get_feature_names()
                                     )
        return [
            self.encode_one_sentence(sentences[index], tf_idf_matrix.iloc[index])
            for index in range(0, len(sentences))
        ]


class UniversalSentenceEmbeddingModel(SentenceEmbeddingModelABC):

    def __init__(self):
        model_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
        self.model = hub.load(model_url)

    def encode(self, sentences: List[str]) -> List:
        return self.model(sentences).numpy().tolist()


class EurLexBertSentenceEmbeddingModel(SentenceEmbeddingModelABC):

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/bert-base-uncased-eurlex")
        self.model = AutoModel.from_pretrained("nlpaueb/bert-base-uncased-eurlex")

    def encode(self, sentences: List[str]) -> List:
        return [
            self.model(**self.tokenizer(sentence, return_tensors='pt'))['pooler_output'].detach().numpy()[0].tolist()
            for sentence in sentences
        ]

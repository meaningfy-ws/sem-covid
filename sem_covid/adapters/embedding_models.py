# -*- coding: utf-8 -*-
# Date    : 20.07.2021 
# Author  : Stratulat Ștefan
# File    : embedding_models.py
# Software: PyCharm
from gensim.models import KeyedVectors

from sem_covid.adapters.abstract_model import EmbeddingModelABC
from sem_covid.services.data_registry import LanguageModel


class Word2VecEmbeddingModel(EmbeddingModelABC):

    def __init__(self):
        law2vec = LanguageModel.LAW2VEC.fetch()
        law2vec_path = LanguageModel.LAW2VEC.path_to_local_cache()
        self.word2vec = KeyedVectors.load_word2vec_format(law2vec_path, encoding="utf-8")

    def encode(self, textual_units: list) -> list:
        return [self.word2vec[word] for word in textual_units if (word in self.word2vec)]


class UniversalSentenceEmbeddingModel(EmbeddingModelABC):

    def __init__(self):
        self.model

    def encode(self, textual_units: list) -> list:
        pass


class DocumentEmbeddingModel(EmbeddingModelABC):

    def encode(self, textual_units: list) -> list:
        pass
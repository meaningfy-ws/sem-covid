# -*- coding: utf-8 -*-
# Date    : 20.07.2021 
# Author  : Stratulat Ștefan
# File    : abstract_model.py
# Software: PyCharm
from abc import ABC, abstractmethod

from typing import List


class TokenizerModelABC(ABC):

    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        raise NotImplementedError


class WordEmbeddingModelABC(ABC):

    @abstractmethod
    def encode(self, tokens: List[str]) -> List:
        raise NotImplementedError


class SentenceEmbeddingModelABC(ABC):

    @abstractmethod
    def encode(self, sentences: List[str]) -> List:
        raise NotImplementedError


class DocumentEmbeddingModelABC(ABC):

    @abstractmethod
    def encode(self, documents: List[str]) -> List:
        raise NotImplementedError

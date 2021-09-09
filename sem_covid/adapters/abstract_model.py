#!/usr/bin/python3

# abstract_model.py
# Date:  21.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from abc import ABC, abstractmethod

from typing import List

"""
    This module aims to define abstractions for different ML models,
     in order to decouple the use of the model and its implementation.
"""


class TokenizerModelABC(ABC):
    """
        This abstraction aims to create a uniform interface for different tokenization approaches.
         The purpose is to disconnect the components dependent on the tokenization method.
    """

    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """
            This method aims to perform tokenization on a text that receives it at the input.
        :param text: the text that is desired to be tokenized
        :return: a token list, where each token is a string
        """
        raise NotImplementedError


class TextSplitterModelABC(ABC):
    """
        This abstract class aims to create a uniform interface for different approaches to dividing text into sequences.
    """

    @abstractmethod
    def split(self, text: str) -> List[str]:
        """
            This method divides the received text into sequences.
        :param text: the text to be divided into sequences
        :return: a list of sequences in the order they appear in the input text
        """


class WordEmbeddingModelABC(ABC):
    """
        This abstraction aims to define an interface for ML models that can encode tokens in embeddings.
    """

    @abstractmethod
    def encode(self, tokens: List[str]) -> List:
        """
            This method is intended to receive a list of tokens and return a list of embeddings.
        :param tokens: a token list, where each token is a string.
        :return: an embedding list, where the position of each embedding corresponds
                    to the position of each token in the input list.
        """
        raise NotImplementedError


class SentenceEmbeddingModelABC(ABC):
    """
        This abstraction aims to define an interface for different approaches to calculating sentence embeddings.
    """

    @abstractmethod
    def encode(self, sentences: List[str]) -> List:
        """
            This method receives a list of sentences, where each sentence represents a string,
             and returns a list of embeddings for each sentence.
        :param sentences: a list of strings, where each string represents a sentence.
        :return: a list of embedding vectors, where each vector is associated
                    with a sentence in the order of the input list.
        """
        raise NotImplementedError


class DocumentEmbeddingModelABC(ABC):
    """
        This abstraction aims to define an interface for different approaches to calculating document embeddings.
    """

    @abstractmethod
    def encode(self, documents: List[str]) -> List:
        """
            This method receives a list of strings, where each string represents a document,
             at the output is returned a list of embedding vectors
             where each vector corresponds to a document in the order of the input list.
        :param documents: a list of documents, based on which document embeddings will be calculated.
        :return: a list of embeddings vectors, where each vector corresponds
                    to a document in the order of the input list.
        """
        raise NotImplementedError

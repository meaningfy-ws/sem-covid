#!/usr/bin/python3

# embedding_models.py
# Date:  21.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from typing import List

import numpy as np
from gensim.models import KeyedVectors

from sem_covid.adapters.abstract_model import (WordEmbeddingModelABC, SentenceEmbeddingModelABC,
                                               TokenizerModelABC)
import tensorflow_hub as hub

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from transformers import AutoTokenizer, TFAutoModel
from tensorflow.python.ops.numpy_ops import np_config

np_config.enable_numpy_behavior()

"""
    This module aims to define concrete implementations for ML model abstractions.
"""


class BasicTokenizerModel(TokenizerModelABC):
    """
        This class is a concrete implementation for TokenizerModelABC,
         where tokenization is done with split operation based on the space character.
    """

    def tokenize(self, text: str) -> List[str]:
        """
            This method performs the tokenization of an input text,
             based on the split operation on the space character.
        :param text: a text that will be tokenized
        :return: a list of tokens, where each token is a string.
        """
        return text.split(' ')


class SpacyTokenizerModel(TokenizerModelABC):
    """
        This class is a concrete implementation,
         which uses a Spacy tokenizer to perform the text tokenization operation.
    """

    def __init__(self, spacy_tokenizer):
        """
            Initializing the tokenizer requires a tokenizer from Spacy.
        :param spacy_tokenizer: a Spacy tokenizer to be used for tokenization.
        """
        self._spacy_tokenizer = spacy_tokenizer

    def tokenize(self, text: str) -> List[str]:
        """
            This method tokenizes the input text and returns a list of tokens where each token is a string.
        :param text: a text that will be tokenized
        :return: a list of tokens, where each token is a string.
        """
        return list(map(str, self._spacy_tokenizer(text)))


class Word2VecEmbeddingModel(WordEmbeddingModelABC):
    """
        This class is a concrete implementation to calculate words embeddings.
    """

    def __init__(self, word2vec: KeyedVectors):
        """
            A gensim KeyedVectors model is required for initialization.
        :param word2vec: un model de type gensim KeyedVectors.
        """
        self._word2vec = word2vec
        self._vector_dimension = word2vec.vector_size

    def encode(self, tokens: List[str]) -> List:
        """
            This method calculates an embedding vector for each token in the list and returns a list of embedding vectors.
        :param tokens: a token list, where each token is a string.
        :return: a list of embeddings vectors, for each token according to the order in the input list.
        """
        return [self._word2vec[word].tolist() if word in self._word2vec else np.zeros(self._vector_dimension).tolist()
                for word in tokens]


class AverageSentenceEmbeddingModel(SentenceEmbeddingModelABC):
    """
        This class represents a concrete implementation for the calculation of embeddings sentences.
        The calculation of embeddings sentences is performed by tokenizing the sentence
         and the calculation of embeddings vectors for each token in the tokenized sentence,
          to then perform the arithmetic mean on the embeddings vectors for tokens,
            the result is an embedding vector for the initial sentence.
    """

    def __init__(self, word_embedding_model: WordEmbeddingModelABC, tokenizer: TokenizerModelABC):
        """
            Initialize the class parameters
        :param word_embedding_model: a word embeddings model
        :param tokenizer: a tokenizer that will be used to tokenize sentences.
        """
        self._word_embedding_model = word_embedding_model
        self._tokenizer = tokenizer

    def encode(self, sentences: List[str]) -> List:
        """
            This method aims to receive a list of sentences and return a list of vector embeddings.
            For each sentence in the input list, the vector embedding will be calculated,
             which will correspond to the order in the output list according
              to the order of the sentences in the input list.
        :param sentences: a list of sentences, where each sentence is a string.
        :return: a list of vector embeddings.
        """
        results = []
        for sentence in sentences:
            embeddings = self._word_embedding_model.encode(self._tokenizer.tokenize(sentence))
            results += [np.mean([np.zeros(len(embeddings[0])).tolist()] + embeddings, axis=0).tolist()]
        return results


class TfIdfSentenceEmbeddingModel(AverageSentenceEmbeddingModel):
    """
        This class represents a concrete implementation for the calculation of embeddings sentences.
        The calculation of embeddings sentences is performed by tokenizing the sentence
         and the calculation of embeddings vectors for each token in the tokenized sentence,
          as later on the basis of words embeddings a weighted average will be made
           where the weight represents the tf-idf metric for each token.
    """

    def encode_one_sentence(self, sentence: str, tf_idf_row: pd.Series) -> List:
        """
            This method encodes a sentence in an embedding vector.
        :param sentence: a sentence that represents a string.
        :param tf_idf_row: a row from tf_idf matrix.
        :return: a vector representing sentence embedding.
        """
        tokens = self._tokenizer.tokenize(sentence)
        embeddings = self._word_embedding_model.encode(tokens)
        sum_weights = 0
        results = [np.zeros(len(embeddings[0]))]
        for index in range(0, len(tokens)):
            if tokens[index] in tf_idf_row.index:
                weight = tf_idf_row[tokens[index]]
                sum_weights += weight
                results += [(weight * np.array(embeddings[index])).tolist()]
        results = np.sum(results, axis=0)
        if sum_weights > 0:
            results = (results / sum_weights)
        return results.tolist()

    def encode(self, sentences: List[str]) -> List:
        """
            This method calculates for the list of input sentences,
             a list of vectors where each vector represents sentence embedding for each sentence in the input list.
        :param sentences: a list of sentences, where each sentence represents a string.
        :return: a list of sentence embeddings.
        """
        tf_idf_vectors = TfidfVectorizer()
        tf_idf_matrix = pd.DataFrame(tf_idf_vectors.fit_transform(sentences).todense().tolist(),
                                     columns=tf_idf_vectors.get_feature_names()
                                     )
        return [
            self.encode_one_sentence(sentences[index], tf_idf_matrix.iloc[index])
            for index in range(0, len(sentences))
        ]


class UniversalSentenceEmbeddingModel(SentenceEmbeddingModelABC):
    """
        This class is a concrete implementation of sentence embedding calculation
         based on Google's Universal Sentence Embeddings.
    """

    def __init__(self):
        """
            Initializing the class parameters,
             namely downloading the pre-trained model from the tensorflow-hub repository.
        """
        model_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
        self.model = hub.load(model_url)

    def encode(self, sentences: List[str]) -> List:
        """
            This method receives a list of sentences, where each sentence represents a string,
             and returns a list of embeddings for each sentence.
        :param sentences: a list of strings, where each string represents a sentence.
        :return: a list of embedding vectors of size 512, where each vector is associated
                    with a sentence in the order of the input list.
        """
        return self.model(sentences).numpy().tolist()


class EurLexBertSentenceEmbeddingModel(SentenceEmbeddingModelABC):
    """
        This class represents a concrete implementation of sentence embedding calculation
         based on the pre-trained BERT model on EurLex.
    """

    def __init__(self):
        """
             Initializing the class parameters,
             namely downloading the pre-trained BERT model on EurLex from the hugging-face repository.
        """
        self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/bert-base-uncased-eurlex")
        self.model = TFAutoModel.from_pretrained("nlpaueb/bert-base-uncased-eurlex")

    def encode(self, sentences: List[str]) -> List:
        """
            This method receives a list of sentences, where each sentence represents a string,
             and returns a list of embeddings for each sentence.
        :param sentences: a list of strings, where each string represents a sentence.
        :return: a list of embedding vectors of size 768, where each vector is associated
                    with a sentence in the order of the input list.
        """
        return [
            self.model(**self.tokenizer(sentence, return_tensors='tf'))['pooler_output'].numpy()[0].tolist()
            for sentence in sentences
        ]

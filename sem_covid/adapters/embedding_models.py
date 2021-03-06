#!/usr/bin/python3

# embedding_models.py
# Date:  21.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com


import torch
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

from typing import List
from more_itertools import windowed
import numpy as np
from gensim.models import KeyedVectors
from sem_covid.adapters.abstract_model import (WordEmbeddingModelABC, SentenceEmbeddingModelABC,
                                               TokenizerModelABC, DocumentEmbeddingModelABC, TextSplitterModelABC)
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re

from sem_covid.services.sc_wrangling.sentences_ranker import textual_tfidf_ranker
import tensorflow_hub as hub
from transformers import AutoTokenizer, TFAutoModel, AutoModel
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


class BasicSentenceSplitterModel(TextSplitterModelABC):
    """
        This class is a concrete implementation of TextSplitterModelABC,
         which divides text into sentences using regular expressions.
    """

    def split(self, text: str) -> List[str]:
        """
            This method divides the received text into sentences.
        :param text: the text to be divided into sentences
        :return: a list of sentences in the order they appear in the input text
        """
        return [sent for sent in re.split("(?<=[\.\!\?;])\s*", text) if sent]


class SpacySentenceSplitterModel(TextSplitterModelABC):
    """
        This class is a concrete implementation of the TextSplitterModelABC interface,
         which uses Spacy's text-splitting model.
    """

    def __init__(self, spacy_nlp):
        """
        :param spacy_nlp:
        """
        self.spacy_nlp = spacy_nlp

    def split(self, text: str) -> List[str]:
        """
            This method divides the received text into sentences.
        :param text: the text to be divided into sentences
        :return: a list of sentences in the order they appear in the input text
        """
        return [sent.text for sent in self.spacy_nlp(text).sents]


class WindowedTextSplitterModel(TextSplitterModelABC):
    """
        This class implements abstraction from TextSplitterModelABC,
         it is dependent on another SentenceSplitter that is not based on the moving window algorithm.
         The purpose of this class is to provide text sequences larger than a sentence,
          these text sequences are obtained by combining a set of sentences.
    """

    def __init__(self, sentence_splitter: TextSplitterModelABC,
                 window_size: int = 10,
                 window_step: int = 5
                 ):
        """
        :param sentence_splitter: a sentence splitter object
        :param window_size: the size of the sentence grouping window
        :param window_step: the step with which the window will be moved to the text
        """
        self.sentence_splitter = sentence_splitter
        self.window_size = window_size
        self.window_step = window_step

    def split(self, text: str) -> List[str]:
        """
            This method aims to divide the text into a list of pieces of text,
            each piece of text represents a set of sentences
        :param text: the text to be divided into pieces
        :return: a list of text sequences
        """
        sentences = self.sentence_splitter.split(text=text)
        windowed_texts = list(
            windowed(sentences,
                     n=self.window_size,
                     fillvalue='',
                     step=self.window_step)
        )
        return [' '.join(window) for window in windowed_texts]


class MovingWindowTextSplitterModel(TextSplitterModelABC):
    """
            This class implements abstraction from TextSplitterModelABC,
         the purpose of this class is to to divide the input text into smaller chunks.
    """

    def __init__(self, window_size: int, window_step: int):
        """
        :param window_size: number of words in each chunk
        :param window_step: moving window step size (also expressed in number of words)
        """
        self.window_size = window_size
        self.window_step = window_step

    def split(self, text: str) -> List[str]:
        """
            This method aims to divide the input text into smaller chunks.
        :param text: the text that should be divided
        :return: a list of text chunks
        """
        chunks = []

        splitted_text = text.split()
        chunk = ' '.join(splitted_text[:self.window_size])

        chunks.append(chunk)

        if len(splitted_text) > self.window_size:

            n = len(splitted_text)

            nr_of_chunks = n // self.window_step

            if n % self.window_step == 0:
                nr_of_chunks = nr_of_chunks - 1

            # start from the second chunk
            for i in range(1, nr_of_chunks):
                chunk = ' '.join(splitted_text[i * self.window_step:i * self.window_step + self.window_size])
                chunks.append(chunk)

        return chunks


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


class TfIdfDocumentEmbeddingModel(DocumentEmbeddingModelABC):
    """
        This class is a concrete implementation of the DocumentEmbeddingModelABC interface,
         the purpose of this class is to calculate document embeddings
          based on the weighted average of embeddings at the level of text sequences.
    """

    def __init__(self, sent_emb_model: SentenceEmbeddingModelABC,
                 sent_splitter: TextSplitterModelABC,
                 top_k: int
                 ):
        """
        :param sent_emb_model: a model for sentence embeddings
        :param sent_splitter: a model for sentence splitter
        :param top_k: the number of important tokens
        """
        self.sent_emb_model = sent_emb_model
        self.sent_splitter = sent_splitter
        self.top_k = top_k

    def encode(self, documents: List[str]) -> List:
        """
            This method aims to generate an embedding for each document in the input list.
        :param documents: list of documents on the basis of which document embeddings will be calculated
        :return: a list of document embeddings
        """
        return [np.average(self.sent_emb_model.encode(document_sentences),
                           axis=0,
                           weights=textual_tfidf_ranker(textual_chunks=document_sentences,
                                                        top_k=self.top_k)
                           )
                for document_sentences in map(self.sent_splitter.split, documents)]


class EurLexBertDocumentEmbeddingModel(DocumentEmbeddingModelABC):
    """
        This class is a concrete implementation of the DocumentEmbeddingModelABC interface,
         the purpose of this class is to calculate embeddings based on splitted documents.
    """

    def __init__(self, text_splitter: TextSplitterModelABC):
        """
        :param tokenizer: the tokenizer used by the below model
        :param model: the model used for computing embeddings
        :param text_splitter: a model for text splitting
        """
        self.tokenizer = AutoTokenizer.from_pretrained('nlpaueb/bert-base-uncased-eurlex')
        self.model = AutoModel.from_pretrained("nlpaueb/bert-base-uncased-eurlex", output_hidden_states=True)
        self.model = self.model.to(device)
        self.text_splitter = text_splitter

    def encode(self, documents: List[str]) -> List:
        """
            This method aims to generate an embedding for each document in the input list.
        :param documents: list of documents on the basis of which document embeddings will be calculated
        :return: a list of document embeddings
        """
        docs_splitted = []

        for doc in documents:
            docs_splitted.append(self.text_splitter.split(doc))

        embeddings = []

        for doc_splitted in docs_splitted:

            tmp_embeddings = []

            for chunk_of_doc in doc_splitted:

                ids_ = self.tokenizer.encode(chunk_of_doc)
                ids_ = torch.LongTensor(ids_)
                ids_ = ids_.unsqueeze(0)
                ids_ = ids_.to(device)

                try:
                    with torch.no_grad():
                        out = self.model(input_ids=ids_)
                # like this we are able to skip the problematic chunks
                except:
                    continue

                hidden_states = out[2]

                last_four_layers = [hidden_states[i] for i in (-1, -2, -3, -4)]

                concat_hidden_states = torch.cat(tuple(last_four_layers), dim=-1)

                tmp_embedding = torch.mean(concat_hidden_states, dim=1).squeeze().cpu().numpy()

                tmp_embeddings.append(tmp_embedding)

            embedding = np.mean(tmp_embeddings, axis=0)

            embeddings.append(embedding)

        return embeddings
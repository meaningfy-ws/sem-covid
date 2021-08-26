
from typing import List

import numpy as np
import spacy
from gensim.models import Word2Vec

from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.token_management import select_pos

nlp = spacy.load('en_core_web_sm')


class POSExtraction:
    """
        Helps to extract the necessary part of speech from word2vec model and handle them
    """
    def __init__(self, word2vec_model: Word2Vec, pos: List[str]) -> None:
        self.word2vec_model = word2vec_model
        self.pos = pos
        self.word2vec_document = None
        self.word2vec_document = nlp(' '.join(self.word2vec_model.wv.index_to_key))
        self.word2vec_document = select_pos(self.word2vec_document, self.pos)
        self._extract_pos = list(map(str, self.word2vec_document))

    def filter_by_pos(self) -> List[str]:
        """
            transforms a word2vec indexes into spacy document and selects parts of
            speech. After that it puts into a list and converts those parts of speech
            into strings.
        """
        return self._extract_pos

    def select_key_words(self, key_words: List[str]) -> List[str]:
        """
            Finds each word form inserted list of key words and returns a
            list with those words if there are presented in the list of
            extracted parts of speech.
        """
        return [word for word in key_words if word in self._extract_pos]

    def extract_pos_index(self) -> List[int]:
        """
            Detects the part of speech indexes and returns them into a list
        """
        return [self.word2vec_model.wv.index_to_key.index(token) for token in self._extract_pos
                if token in self.word2vec_model.wv.index_to_key]

    def extract_pos_embeddings(self) -> np.ndarray:
        """
            Detects part of speech embeddings from their indexes
        """
        selected_pos_index = self.extract_pos_index()
        return np.array([self.word2vec_model.wv.vectors[index] for index in selected_pos_index])

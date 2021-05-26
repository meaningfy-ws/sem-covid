
from typing import List

import pandas as pd
from gensim.models import LdaMulticore
import gensim.corpora as corpora


class WordsModeling(object):

    def __init__(self, document: List):
        self.document = document
        self.id2word = corpora.Dictionary(self.document)
        self.corpus = [self.id2word.doc2bow(text) for text in self.document]

    def lda_model_training(self) -> LdaMulticore:
        """
        create topic model based on input document
        """
        return LdaMulticore(corpus=self.corpus, id2word=self.id2word, num_topics=10, random_state=100, chunksize=10,
                            passes=10, alpha="symmetric", iterations=100, per_word_topics=True)

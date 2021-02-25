import numpy as np
from gensim.models import Word2Vec

import pathlib
FOLDER = pathlib.Path("/home/jovyan/work/upload/")
LAW2VEC_PATH = '/home/jovyan/work/upload/data/law2vec/Law2Vec.200d.txt'

# Insert our data and set minimal word count to 10, and size of each word to 300 vectors
model = Word2Vec.load('/home/jovyan/work/Dan/data/pwdb/word2vec/df.model')
w2v_dict = {w: vec for w, vec in zip(model.wv.index2word, model.wv.syn0)}


class MeanEmbeddingVectorizerWord2Vec(object):
    """Calculate the mean of each word"""
    def __init__(self, word2vec):
        self.word2vec = word2vec
        if len(word2vec) > 0:
            self.dim = len(word2vec[next(iter(w2v_dict))])
        else:
            self.dim = 0

    def fit(self, X, y):
        return self

    def transform(self, X):
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0) for words in X]
        )


class MeanEmbeddingVectorizerLaw2Vec(object):
    """Calculate the mean of each word"""
    def __init__(self, word2vec):
        self.word2vec = word2vec
        if len(word2vec) > 0:
            self.dim = len(word2vec[next(iter(LAW2VEC_PATH))])
        else:
            self.dim = 0

    def fit(self, X, y):
        return self

    def transform(self, X):
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0) for words in X]
        )
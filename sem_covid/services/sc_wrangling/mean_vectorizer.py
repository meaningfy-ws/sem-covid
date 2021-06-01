import numpy as np
from gensim.models import Word2Vec


class MeanEmbeddingVectorizer(object):
    """Calculate the mean of each word"""

    def __init__(self, word2vec):
        self.word2vec = word2vec
        if len(word2vec) > 0:
            self.dim = len(word2vec[next(iter(word2vec))])
        else:
            self.dim = 0

    def fit(self, X, y):
        return self

    def transform(self, X):
        # TODO: Why we have array of arrays?
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0) for words in X]
        )


def text_to_vector(text: str, word2vec):
    return np.mean([word2vec[word] for word in text.split() if word in word2vec], axis=0)


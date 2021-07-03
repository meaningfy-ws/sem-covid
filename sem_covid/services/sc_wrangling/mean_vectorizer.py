import numpy as np


def text_to_vector(text: str, word2vec):
    dim = word2vec.vectors.shape[1]
    result = [word2vec[word] for word in text.split() if (word in word2vec)]
    return np.mean([np.zeros(dim)] + result, axis=0)

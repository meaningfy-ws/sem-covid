import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
from scipy.spatial.distance import squareform, pdist
from sklearn.metrics import pairwise_distances


def euclidean_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate euclidean similarity between two vectors
    """
    return 1 / (1 + np.linalg.norm(vector_1 - vector_2))


def cosine_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate cosine similarity between two vectors
    """
    return np.dot(vector_1, vector_2) / (np.linalg.norm(vector_1) * np.linalg.norm(vector_2))


def manhattan_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate manhattan similarity between two vectors
    """
    return 1 / (1 + np.sum(np.abs(vector_1 - vector_2)))


def build_similarity_matrix(vector: np.ndarray, keys: list, metric: str) -> pd.DataFrame:
    """
        creates a dataframe based on keys and vectors from pretrained gensim model
        and selected similarity function

        :param vector: the object that contains the mapping between words and embeddings
        :param keys: words indexes keys
        :param metric: metric distance formula
        :return: dataframe with similarity of each word
    """
    result_df = pd.DataFrame(squareform(pdist(vector.astype('float16'), metric=metric)), columns=keys, index=keys)
    result_df = result_df.astype('float16')
    return result_df

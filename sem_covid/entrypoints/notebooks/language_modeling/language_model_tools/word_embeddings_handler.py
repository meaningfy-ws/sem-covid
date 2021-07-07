
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
from sklearn.manifold import TSNE


def select_words_and_embedding_clusters(word2vec_model: KeyedVectors, key_words: list) -> tuple:
    """
        This function finds top 30 most similar words from inserted key words and
        insert their clusters into arrays
    """
    embedding_clusters = []
    word_clusters = []

    for word in key_words:
        embedding = []
        words = []

        for similar_word, word_vector in word2vec_model.most_similar(word, topn=30):
            words.append(similar_word)
            embedding.append(word2vec_model[similar_word])

        embedding_clusters.append(embedding)
        word_clusters.append(words)

    return embedding_clusters, word_clusters


def create_tsne_model(word_embeddings: list) -> np.ndarray:
    """
        Creates TSNE model based on inserted word embeddings
        TSNE arguments:
          :perplexity: The number of nearest neighbors that is used in other manifold learning algorithms
          :n_components: Dimension of the embedded space
          :init: Initialization of embedding
          :n_iter: Maxim number of iterations for the optimization (!!! At least 250 !!!)
          :random_state: Determines the random number generator
    """
    word_embedding_clusters = np.array(word_embeddings)
    axis_0, axis_1, axis_2 = word_embedding_clusters.shape
    tsne_model_specific_words = TSNE(perplexity=15, n_components=2, init='pca', n_iter=3500, random_state=32)

    return tsne_model_specific_words.fit_transform(word_embedding_clusters.reshape(axis_0 * axis_1, axis_2))


def create_word_clusters_matrix(key_words: list, word_clusters: list, tsne_words_model: np.ndarray) -> pd.DataFrame:
    """
        Creates a dataframe that show words vector representation on a graph
    """
    specific_words_dataframe = pd.DataFrame(
        {'word_cluster': key_words, 'word': word_clusters},
        columns=['word_cluster', 'word']).explode('word').reset_index(drop=True)
    dataframe_vectors = pd.DataFrame(tsne_words_model, columns=['X', 'Y'])

    return pd.concat([specific_words_dataframe, dataframe_vectors], axis=1)

import numpy as np
import pandas as pd

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.word_embeddings_handler import (
    create_word_clusters_matrix, create_tsne_model, select_words_and_embedding_clusters)


def test_select_words_and_embedding_clusters(common_word2vec_model):
    words = ['system', 'graph']

    words_embedding_clusters = select_words_and_embedding_clusters(common_word2vec_model.wv, words)

    assert tuple == type(words_embedding_clusters)
    assert list == type(words_embedding_clusters[0])
    assert list == type(words_embedding_clusters[1])
    assert np.ndarray == type(words_embedding_clusters[0][0][0])
    assert str == type(words_embedding_clusters[1][0][0])
    assert ['computer', 'response', 'human', 'interface', 'survey',
            'time', 'graph', 'minors', 'trees', 'eps', 'user'] == words_embedding_clusters[1][0]
    assert ['user', 'survey', 'eps', 'human', 'minors', 'system',
            'trees', 'computer', 'time', 'response', 'interface'] == words_embedding_clusters[1][1]


def test_create_tsne_model(common_word2vec_model):
    words = ['system', 'graph']
    words_embedding_clusters = select_words_and_embedding_clusters(common_word2vec_model.wv, words)
    tsne_model = create_tsne_model(words_embedding_clusters[0])

    assert np.ndarray == type(tsne_model)


def test_create_word_clusters_matrix(common_word2vec_model):
    words = ['system', 'graph']
    words_embedding_clusters = select_words_and_embedding_clusters(common_word2vec_model.wv, words)
    tsne_model = create_tsne_model(words_embedding_clusters[0])
    words_cluster_dataframe = create_word_clusters_matrix(words, words_embedding_clusters[1], tsne_model)

    assert pd.DataFrame == type(words_cluster_dataframe)
    assert 22 == len(words_cluster_dataframe)
    assert ['word_cluster', 'word', 'X', 'Y'] == list(words_cluster_dataframe.columns)



from gensim.models import Word2Vec
from gensim.test.utils import common_texts

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.similarity_calculus import *

vector1 = np.array([2, 4, 4, 6])
vector2 = np.array([5, 5, 7, 8])


def test_euclidean_similarity():
    similarity_coefficient = euclidean_similarity(vector1, vector2)

    assert np.float64 == type(similarity_coefficient)
    assert 0.17253779651421453 == similarity_coefficient


def test_cosine_similarity():
    similarity_coefficient = cosine_similarity(vector1, vector2)

    assert np.float64 == type(similarity_coefficient)
    assert 0.9784661702650235 == similarity_coefficient


def test_manhattan_similarity():
    similarity_coefficient = manhattan_similarity(vector1, vector2)

    assert np.int64 == type(similarity_coefficient)
    assert 9 == similarity_coefficient


def test_get_similarity_matrix():
    model = Word2Vec(sentences=common_texts, vector_size=100, window=5, min_count=1, workers=4)
    similarity_matrix = get_similarity_matrix(model.wv, similarity_function=cosine_similarity)

    assert pd.DataFrame == type(similarity_matrix)
    assert 12 == len(similarity_matrix)
    assert [('system',), ('graph',), ('trees',), ('user',),
            ('minors',), ('eps',), ('time',), ('response',),
            ('survey',), ('computer',), ('interface',), ('human',)] == list(similarity_matrix.index)
    assert ['system', 'graph', 'trees', 'user', 'minors', 'eps',
            'time', 'response', 'survey', 'computer', 'interface', 'human'] == list(similarity_matrix.columns)
    assert np.float64 == type(similarity_matrix['system'][0])
    assert 1.0 == similarity_matrix['system'][0]

import pickle

from gensim.models import Word2Vec
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from networkx.exception import NetworkXError
import numpy as np
from d3graph import d3graph

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.graph_handling import generate_graph
from sem_covid.services.store_registry import store_registry

import timeit

start = timeit.default_timer()

BUCKET_NAME = 'semantic-similarity-matrices'

DELIMITER = '_'
FILE_FORMAT = '.pkl'
MATRIX_TYPE_NAME = '_matrix'

# streamlit widgets' names
STREAMLIT_TITLE = 'Semantic similarity graph'
TEXT_INPUT_WIDGET = "Introduce word"
MODEL_INPUT_WIDGET = 'Select the model'
MATRIX_TEXT_INPUT = "Select similarity"
BUTTON_NAME = 'Generate graph'


def cosine_normalize(x):
    return 1 - x


def std_normalize(x):
    return 1 / (1 + x)


MODELS = ('model1', 'model2', 'model3')
SIMILARITIES = ('cosine', 'euclidean')
NORMALIZERS = (cosine_normalize, std_normalize)


def load_data_in_cache():
    if not hasattr(st, 'easy_cache'):
        minio_feature_store = store_registry.minio_feature_store(BUCKET_NAME)
        st.easy_cache = dict()
        for model in MODELS:
            for similarity, normalizer in zip(SIMILARITIES, NORMALIZERS):
                cache_key = model + DELIMITER + similarity + MATRIX_TYPE_NAME + FILE_FORMAT
                st.easy_cache[cache_key] = minio_feature_store.get_features(features_name=cache_key).applymap(normalizer)
    return st.easy_cache


app_cache = load_data_in_cache()


def create_similarity_graph(similarity_matrix: pd.DataFrame, key_word: str, metric_threshold: np.float64,
                            top_words: int) -> d3graph:
    color_map = {0: '#F38BA0',
                 1: '#3DB2FF',
                 2: '#FFB830',
                 3: '#FF2442'}
    deep_map = {}

    graph = generate_graph(nx.Graph(), similarity_matrix, key_word, top_words=top_words,
                           threshold=metric_threshold, deep_map=deep_map, color_map=color_map)
    network_adjacency_matrix = pd.DataFrame(data=nx.adjacency_matrix(graph).todense(),
                                            index=graph.nodes(), columns=graph.nodes())
    node_color_list = [deep_map[node][0] for node in graph.nodes()]
    return d3graph(network_adjacency_matrix, node_color=node_color_list, node_color_edge='FFEDDA',
                   width=650, height=500, edge_width=5, edge_distance=60, directed=True, showfig=False)


st.title(STREAMLIT_TITLE)

col1, col2, col3 = st.columns(3)

model_number = col1.selectbox(
    MODEL_INPUT_WIDGET,
    MODELS
)

matrix = col2.selectbox(
    MATRIX_TEXT_INPUT,
    SIMILARITIES)

selected_key = (model_number + DELIMITER + matrix + MATRIX_TYPE_NAME + FILE_FORMAT)

word = col3.selectbox(
    TEXT_INPUT_WIDGET,
    app_cache[selected_key].columns.to_list())

threshold_slider = st.slider('Threshold', min_value=0.0, max_value=1.0, step=0.05, value=0.4)
number_of_neighbours_slider = st.slider('Number of Neighbours', min_value=2, max_value=5, step=1, value=1)

if st.button(BUTTON_NAME):
    try:
        st.write('Generating graph . . .')
        components.html(open(create_similarity_graph(
            similarity_matrix=app_cache[selected_key],
            key_word=word, top_words=number_of_neighbours_slider + 1,
            metric_threshold=threshold_slider)['path'], 'r', encoding='utf-8').read(), width=700, height=700)
    except KeyError:
        st.write('There is no such a word.')
    except ValueError:
        st.write('There are no similar words in this threshold range. '
                 'Please decrease the number.')
    except NetworkXError:
        st.write('Graph has no nodes or edges.')
    except IndexError:
        st.write('Please select an option. ')

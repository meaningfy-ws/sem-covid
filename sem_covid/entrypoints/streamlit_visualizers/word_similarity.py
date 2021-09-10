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

BUCKET_NAME = 'semantic-similarity-matrices'

# model names
MODEL1 = 'model1'
MODEL2 = 'model2'
MODEL3 = 'model3'

DELIMITER = '_'
FILE_FORMAT = '.pkl'
COSINE_MATRIX = 'cosine'
EUCLIDEAN_MATRIX = 'euclidean'
MATRIX_TYPE_NAME = '_matrix'
HAMMING_MATRIX = 'hamming'

# streamlit widgets' names
STREAMLIT_TITLE = 'Semantic similarity graph'
TEXT_INPUT_WIDGET = "Introduce word"
MODEL_INPUT_WIDGET = 'Select the model'
MATRIX_TEXT_INPUT = "Select similarity"
BUTTON_NAME = 'Generate graph'


@st.cache(suppress_st_warning=True, show_spinner=False)
def read_similarity_matrix(similarity_matrix: str, bucket_name: str = BUCKET_NAME) -> pd.DataFrame:
    """
        It goes in MinIO and gets the necessary matrix from the bucket
    """
    if COSINE_MATRIX in similarity_matrix:
        return store_registry.minio_feature_store(bucket_name).get_features(similarity_matrix).applymap(lambda x: 1 - x)
    elif EUCLIDEAN_MATRIX in similarity_matrix:
        return store_registry.minio_feature_store(bucket_name).get_features(similarity_matrix).applymap(
            lambda x: 1 / (1 + x))
    elif HAMMING_MATRIX in similarity_matrix:
        return store_registry.minio_feature_store(bucket_name).get_features(similarity_matrix).applymap(
            lambda x: 1 / (1 + x))


@st.cache(suppress_st_warning=True, show_spinner=False)
def read_language_model(bucket_name: str, language_model_name: str) -> Word2Vec:
    """
        It goes in MinIO and gets the language model from the bucket
    """
    return pickle.loads(store_registry.minio_object_store(bucket_name).get_object(language_model_name))


@st.cache(suppress_st_warning=True, show_spinner=False)
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
    (MODEL1, MODEL2, MODEL3)
)

matrix = col2.selectbox(
    MATRIX_TEXT_INPUT,
    (COSINE_MATRIX, EUCLIDEAN_MATRIX, HAMMING_MATRIX))

word = col3.selectbox(
    TEXT_INPUT_WIDGET,
    read_similarity_matrix((model_number + DELIMITER + matrix + MATRIX_TYPE_NAME + FILE_FORMAT)).columns.to_list())

threshold_slider = st.slider('Threshold', min_value=0.0, max_value=1.0, step=0.05, value=0.4)
number_of_neighbours_slider = st.slider('Number of Neighbours', min_value=2, max_value=5, step=1, value=1)

if st.button(BUTTON_NAME):
    try:
        st.write('Generating graph . . .')
        components.html(open(create_similarity_graph(
            similarity_matrix=read_similarity_matrix(
                model_number + DELIMITER + matrix + MATRIX_TYPE_NAME + FILE_FORMAT),
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

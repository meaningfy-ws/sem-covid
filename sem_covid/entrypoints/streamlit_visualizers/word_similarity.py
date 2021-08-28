
import pickle

from gensim.models import Word2Vec
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from networkx.exception import NetworkXError
import numpy as np
from d3graph import d3graph

from sem_covid.services.store_registry import store_registry


BUCKET_NAME = 'semantic-similarity-matrices'
MODEL_NUMBER = 'model2_'
FILE_FORMAT = '.pkl'
COSINE_MATRIX = 'cosine'
EUCLIDEAN_MATRIX = 'euclidean'
HAMMING_MATRIX = 'hamming'
STREAMLIT_TITLE = 'Semantic similarity graph'
TEXT_INPUT_WIDGET = "Introduce word"
MATRIX_TEXT_INPUT = "Select similarity"
BUTTON_NAME = 'Generate graph'
LANGUAGE_MODEL_BUCKET_NAME = 'mdl-language'
LANGUAGE_MODEL_NAME = 'word2vec/model2_language_model.model'


@st.cache(suppress_st_warning=True, show_spinner=False)
def read_similarity_matrix(similarity_matrix: str, bucket_name: str = BUCKET_NAME) -> pd.DataFrame:
    """
        It goes in MinIO and gets the necessary matrix from the bucket
    """
    if COSINE_MATRIX in similarity_matrix:
        return store_registry.minio_feature_store(bucket_name).get_features(similarity_matrix).applymap(lambda x: 1 - x)
    elif EUCLIDEAN_MATRIX in similarity_matrix:
        return store_registry.minio_feature_store(bucket_name).get_features(similarity_matrix).applymap(lambda x: 1 / (1 + x))
    elif HAMMING_MATRIX in similarity_matrix:
        return store_registry.minio_feature_store(bucket_name).get_features(similarity_matrix).applymap(lambda x: 1 / (1 + x))


@st.cache(suppress_st_warning=True, show_spinner=False)
def read_language_model(bucket_name: str, language_model_name: str) -> Word2Vec:
    """
        It goes in MinIO and gets the language model from the bucket
    """
    return pickle.loads(store_registry.minio_object_store(bucket_name).get_object(language_model_name))


@st.cache(suppress_st_warning=True, show_spinner=False)
def generate_graph(similarity_matrix: pd.DataFrame, graph: nx.Graph, root_word: str,
                   top_words: int, threshold: np.float64 = 0.8, deep_level: int = 0,
                   max_deep_level: int = 2, deep_map: dict = None, color_map: dict = None) -> nx.Graph:
    """
        Generates d3 graph using the inserted keywords and their top words from similarity matrix
    Args:
        similarity_matrix: Dataframe with word similarity
        graph: networkx graph
        root_word: key words
        top_words: top similar words from inserted keywords
        threshold: minimum percentage of similarity
        deep_level: the level of generating leaf
        max_deep_level: the maximum number of generated leaf
        deep_map: dictionary of the words and their level of similarity
        color_map: the color of each level of words' similarity

    Returns: a d3 graph with title and root of key word and their similarity words
    """
    if root_word not in deep_map.keys():
        deep_map[root_word] = (deep_level, color_map[deep_level])
    elif deep_map[root_word][0] > deep_level:
        deep_map[root_word] = (deep_level, color_map[deep_level])
    if deep_level > max_deep_level:
        return graph
    new_nodes = similarity_matrix[root_word].sort_values(ascending=False)[:top_words].index.to_list()
    new_nodes_weight = list(similarity_matrix[root_word].sort_values(ascending=False)[:top_words].values)
    for index in range(0, len(new_nodes)):
        if new_nodes_weight[index] >= threshold:
            graph.add_edge(root_word, new_nodes[index])
            generate_graph(similarity_matrix, graph, new_nodes[index], top_words, threshold, deep_level + 1,
                           max_deep_level,
                           deep_map=deep_map, color_map=color_map)

    return graph


@st.cache(suppress_st_warning=True, show_spinner=False)
def create_similarity_graph(similarity_matrix: pd.DataFrame, key_word: str, metric_threshold: np.float64,
                            top_words: int) -> d3graph:
    color_map = {0: '#F38BA0',
                 1: '#3DB2FF',
                 2: '#FFB830',
                 3: '#FF2442'}
    deep_map = {}
    graph = generate_graph(similarity_matrix, nx.Graph(), key_word,
                           top_words=top_words, threshold=metric_threshold,
                           deep_map=deep_map, color_map=color_map)
    network_adjacency_matrix = pd.DataFrame(data=nx.adjacency_matrix(graph).todense(),
                                            index=graph.nodes(), columns=graph.nodes())
    node_color_list = [deep_map[node][0] for node in graph.nodes()]
    return d3graph(network_adjacency_matrix, node_color=node_color_list, node_color_edge='FFEDDA',
                   width=650, height=500, edge_width=5, edge_distance=60, directed=True, showfig=False)


st.title(STREAMLIT_TITLE)

col1, col2 = st.columns(2)

word = col1.multiselect(
    TEXT_INPUT_WIDGET,
    read_language_model(LANGUAGE_MODEL_BUCKET_NAME, LANGUAGE_MODEL_NAME).wv.index_to_key)

matrix = col2.selectbox(
    MATRIX_TEXT_INPUT,
    (COSINE_MATRIX, EUCLIDEAN_MATRIX, HAMMING_MATRIX))


threshold_slider = st.slider('Threshold', min_value=0.0, max_value=1.0, step=0.05, value=0.4)
number_of_neighbours_slider = st.slider('Number of Neighbours', min_value=2, max_value=5, step=1, value=1)


if st.button(BUTTON_NAME):
    try:
        st.write('Generating graph . . .')
        components.html(open(create_similarity_graph(
            similarity_matrix=read_similarity_matrix(MODEL_NUMBER + matrix + '_matrix' + FILE_FORMAT),
            key_word=word[0], top_words=number_of_neighbours_slider + 1,
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

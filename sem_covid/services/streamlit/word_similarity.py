
import streamlit as st
from streamlit.components import v1 as components
import pandas as pd
import networkx as nx
import numpy as np
from d3graph import d3graph

from sem_covid.services.store_registry import store_registry

BUCKET_NAME = 'semantic-similarity-matrices'
MODEL_NAME = 'model2_cosine_matrix.json'


@st.cache
def read_similarity_matrix(bucket_name: str, similarity_matrix: str) -> pd.DataFrame:
    return pd.read_json(store_registry
                        .minio_object_store(bucket_name)
                        .get_object(similarity_matrix)).applymap(lambda x: 1 - x)


@st.cache
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


@st.cache
def create_similarity_graph(similarity_matrix: pd.DataFrame, key_word: str, metric_threshold: np.float64,
                            top_words: int) -> d3graph:
    color_map = {0: '#a70000',
                 1: '#f0000',
                 2: '#ff7b7b',
                 3: '#ffbaba'}
    deep_map = {}
    graph = generate_graph(similarity_matrix, nx.Graph(), key_word,
                           top_words=top_words, threshold=metric_threshold,
                           deep_map=deep_map, color_map=color_map)
    network_adjacency_matrix = pd.DataFrame(data=nx.adjacency_matrix(graph).todense(),
                                            index=graph.nodes(), columns=graph.nodes())
    node_color_list = [deep_map[node][0] for node in graph.nodes()]
    return d3graph(network_adjacency_matrix, node_color=node_color_list, width=1920, height=1080, edge_width=5,
                   edge_distance=60, directed=True)


st.title('Semantic similarity graph')

word = st.text_input("Introduce word")

threshold_slider = st.slider('Threshold', min_value=0.0, max_value=1.0, step=0.1, value=0.4)
number_of_neighbours_slider = st.slider('Number of Neighbours', min_value=1, max_value=5, step=1, value=1)
# graph_depth_slider = st.slider('Graph Depth', min_value=2, max_value=5, step=1, value=0)


st.write(word)

sliders = [threshold_slider, number_of_neighbours_slider]

for slider in sliders:
    st.write(slider)


if st.button('generate'):
    create_similarity_graph(similarity_matrix=read_similarity_matrix(BUCKET_NAME, MODEL_NAME),
                            key_word=word, top_words=number_of_neighbours_slider,
                            metric_threshold=threshold_slider)




import networkx as nx

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.graph_handling import (
    generate_graph)


def test_generate_graph(mock_similarity_matrix):
    color_map = {0: '#a70000',
                 1: '#f0000',
                 2: '#ff7b7b',
                 3: '#ffbaba'}
    deep_map = {}
    root_word = 'parliament'
    top_words = 2
    graph = generate_graph(mock_similarity_matrix, root_word, top_words, deep_map=deep_map, color_map=color_map)
    assert nx.Graph == type(graph)
    assert ['parliament'] == list(graph.nodes)
    assert [('parliament', 'parliament')] == list(graph.edges)

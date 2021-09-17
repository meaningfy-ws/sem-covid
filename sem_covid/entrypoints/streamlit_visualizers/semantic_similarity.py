#!/usr/bin/python3

# semantic_similarity.py
# Date:  17.09.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import pickle
from typing import Any, List

from gensim.models import Word2Vec
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from more_itertools import unique_everseen
from networkx.exception import NetworkXError
import numpy as np
from d3graph import d3graph
from numpy import mean
from sklearn.metrics.pairwise import cosine_similarity

from sem_covid import config
from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.graph_handling import generate_graph
from sem_covid.services.model_registry import embedding_registry
from sem_covid.services.store_registry import store_registry
import plotly.express as px

UNIFIED_DATASET = 'ds_unified_datasets'


def load_data_in_cache():
    if not hasattr(st, 'easy_cache'):
        es_store = store_registry.es_index_store()
        st.easy_cache = dict()
        st.easy_cache['pwdb_df'] = es_store.get_dataframe(index_name=config.PWDB_ELASTIC_SEARCH_INDEX_NAME)
        unified_df = es_store.get_dataframe(index_name=UNIFIED_DATASET)
        emb_model = embedding_registry.sent2vec_universal_sent_encoding()
        unified_df = pd.DataFrame(unified_df[unified_df.Document_source == 'pwdb'])
        unified_df['text'] = unified_df[['Title', 'Content']].agg(' '.join, axis=1)
        unified_df['emb'] = emb_model.encode(unified_df['text'].values)
        st.easy_cache['unified_df'] = unified_df
        st.write('Data cached!')
    return st.easy_cache


app_cache = load_data_in_cache()


def prepare_df(unified_df: pd.DataFrame,
               pwdb_df: pd.DataFrame,
               column_filter_name: str,
               column_filter_value: Any
               ):
    search_index = pwdb_df[pwdb_df[column_filter_name] == column_filter_value].index.values
    result_df = pd.DataFrame(unified_df[unified_df.index.isin(search_index)])
    return result_df


def top_k_mean(data: np.array, top_k: int):
    tmp_data = data.copy().tolist()
    tmp_data.sort(reverse=True)
    return mean(tmp_data[:top_k] + [0] * (top_k - len(data)))


def generate_countries_similarity_matrix(unified_df: pd.DataFrame,
                                         pwdb_df: pd.DataFrame,
                                         countries: List[str]):
    n = len(countries)
    sim_matrix = np.zeros((n, n))
    for i in range(0, len(countries)):
        sim_matrix[i][i] = 0
        df_x = prepare_df(unified_df=unified_df,
                          pwdb_df=pwdb_df,
                          column_filter_name='country',
                          column_filter_value=countries[i]
                          )
        for j in range(i + 1, len(countries)):
            df_y = prepare_df(unified_df=unified_df,
                              pwdb_df=pwdb_df,
                              column_filter_name='country',
                              column_filter_value=countries[j]
                              )

            x_values = list(df_x['emb'].values.tolist())
            tmp_sim_matrix = cosine_similarity(x_values,
                                               df_y['emb'].values.tolist())
            sim_mean = top_k_mean(tmp_sim_matrix[np.triu_indices_from(tmp_sim_matrix, k=1)], 50)
            sim_matrix[i][j] = sim_matrix[j][i] = sim_mean
    return sim_matrix


def main():
    pwdb_df = app_cache['pwdb_df']
    unified_df = app_cache['unified_df']
    countries = list(unique_everseen(pwdb_df.country.values))
    st.title('Semantic similarity')
    countries_similarity_matrix = generate_countries_similarity_matrix(unified_df=unified_df, pwdb_df=pwdb_df,
                                                                       countries=countries)
    fig = px.imshow(countries_similarity_matrix,
                    labels=dict(color="Semantic similarity"),
                    x=countries,
                    y=countries,
                    width=700,
                    height=700
                    )
    fig.update_xaxes(side="top")
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()

#     col1, col2 = st.columns(2)
#
#     country_1 = col1.selectbox(
#         MODEL_INPUT_WIDGET,
#         MODELS
#     )
#
# matrix = col2.selectbox(
#     MATRIX_TEXT_INPUT,
#     SIMILARITIES)
#
# selected_key = (model_number + DELIMITER + matrix + MATRIX_TYPE_NAME + FILE_FORMAT)
#
# # word = col3.selectbox(
# #     TEXT_INPUT_WIDGET,
# #     app_cache[selected_key].columns.to_list())
#
# threshold_slider = st.slider('Threshold', min_value=0.0, max_value=1.0, step=0.05, value=0.4)
# number_of_neighbours_slider = st.slider('Number of Neighbours', min_value=2, max_value=5, step=1, value=1)
# #
# if st.button(BUTTON_NAME):
#     try:
#         st.write('Generating graph . . .')
#         components.html(open(create_similarity_graph(
#             similarity_matrix=app_cache[selected_key],
#             key_word=word, top_words=number_of_neighbours_slider + 1,
#             metric_threshold=threshold_slider)['path'], 'r', encoding='utf-8').read(), width=700, height=700)
#     except KeyError:
#         st.write('There is no such a word.')
#     except ValueError:
#         st.write('There are no similar words in this threshold range. '
#                  'Please decrease the number.')
#     except NetworkXError:
#         st.write('Graph has no nodes or edges.')
#     except IndexError:
#         st.write('Please select an option. ')

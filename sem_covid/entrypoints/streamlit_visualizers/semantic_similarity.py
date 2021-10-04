#!/usr/bin/python3

# semantic_similarity.py
# Date:  17.09.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from datetime import datetime
from typing import Any, List

import streamlit as st
import pandas as pd
from more_itertools import unique_everseen
import numpy as np
from numpy import mean
from sklearn.metrics.pairwise import cosine_similarity

from sem_covid import config
from sem_covid.services.model_registry import embedding_registry
from sem_covid.services.store_registry import store_registry
import plotly.express as px


def load_data_in_cache():
    if not hasattr(st, 'easy_cache'):
        es_store = store_registry.es_index_store()
        st.easy_cache = dict()
        st.easy_cache['unified_df'] = #es_store.get_dataframe(index_name=config.UNIFIED_DATASET_ELASTIC_SEARCH_INDEX_NAME)
        st.write('Data cached!')
    return st.easy_cache


app_cache = load_data_in_cache()
unified_df = app_cache['unified_df']
countries = list(unique_everseen(unified_df.country.values))


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
                                         countries: List[str],
                                         number_of_docs: int
                                         ):
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
            tmp_sim_matrix = cosine_similarity(df_x['emb'].values.tolist(),
                                               df_y['emb'].values.tolist())
            sim_mean = top_k_mean(tmp_sim_matrix[np.triu_indices_from(tmp_sim_matrix, k=1)], number_of_docs)
            sim_matrix[i][j] = sim_matrix[j][i] = sim_mean
    return sim_matrix


def generate_2_country_similarity_matrix(data_x: pd.DataFrame, data_y: pd.DataFrame,
                                         start_date: str, end_date: str, periods: int, number_of_docs: int):
    data_x['Date'] = pd.to_datetime(data_x['Date']).dt.date
    data_y['Date'] = pd.to_datetime(data_y['Date']).dt.date
    time_periods = pd.date_range(start=start_date,
                                 end=end_date,
                                 periods=periods).to_pydatetime().tolist()
    time_periods = list(map(lambda x: x.date(), time_periods))
    time_periods = list(zip(time_periods, time_periods[1:]))
    n = len(time_periods)
    sim_matrix = np.zeros((n, n))
    for i in range(0, n):
        start_y, end_y = time_periods[i]
        tmp_df_y = data_y[(data_y['Date'] >= start_y) & (data_y['Date'] < end_y)]
        if len(tmp_df_y):
            for j in range(0, n):
                start_x, end_x = time_periods[j]
                tmp_df_x = data_x[(data_x['Date'] >= start_x) & (data_x['Date'] < end_x)]
                if len(tmp_df_x):
                    tmp_sim_matrix = cosine_similarity(tmp_df_x['emb'].values.tolist(),
                                                       tmp_df_y['emb'].values.tolist())
                    sim_mean = top_k_mean(tmp_sim_matrix[np.triu_indices_from(tmp_sim_matrix, k=1)], number_of_docs)
                    sim_matrix[i][j] = sim_mean
    return sim_matrix, time_periods


def menu_countries_similarity():
    number_of_docs = st.slider('Number of documents', min_value=1, max_value=50, step=1, value=10)

    # if st.button('Plot similarity'):
    #     countries_similarity_matrix = generate_countries_similarity_matrix(unified_df=unified_df, pwdb_df=pwdb_df,
    #                                                                        countries=countries,
    #                                                                        number_of_docs=number_of_docs)
    #     fig = px.imshow(countries_similarity_matrix,
    #                     labels=dict(color="Semantic similarity"),
    #                     x=countries,
    #                     y=countries,
    #                     width=700,
    #                     height=700
    #                     )
    #     fig.update_xaxes(side="top")
    #     st.plotly_chart(fig)


def menu_time_period_similarity():
    col1, col2, col3, col4 = st.columns(4)
    # country_1 = col1.selectbox('First country', countries)
    # country_2 = col2.selectbox('Second country', countries)
    # start_date = str(col3.date_input('start date', value=datetime(2020, 1, 1),
    #                                  min_value=datetime(2020, 1, 1),
    #                                  max_value=datetime(2021, 6, 1)))
    # end_date = str(col4.date_input('end date', value=datetime(2021, 6, 1),
    #                                min_value=datetime(2020, 1, 1),
    #                                max_value=datetime(2021, 6, 1)))
    # number_of_periods = st.slider('Periods', min_value=1, max_value=12, step=1, value=6)
    # number_of_docs = st.slider('Number of documents', min_value=1, max_value=50, step=1, value=10)
    # if st.button('Generate similarity'):
    #     df_x = prepare_df(unified_df=unified_df,
    #                       pwdb_df=pwdb_df,
    #                       column_filter_name='country',
    #                       column_filter_value=country_1
    #                       )
    #     df_y = prepare_df(unified_df=unified_df,
    #                       pwdb_df=pwdb_df,
    #                       column_filter_name='country',
    #                       column_filter_value=country_2)
    #     tmp_sim_matrix, tmp_periods = generate_2_country_similarity_matrix(df_x, df_y, start_date=start_date,
    #                                                                        end_date=end_date, periods=number_of_periods,
    #                                                                        number_of_docs = number_of_docs
    #                                                                        )
    #     tmp_periods = [' '.join([str(x), str(y)]) for x, y in tmp_periods]
    #     color_scheme = [(0, "orange"),
    #                     (0.5, "yellow"),
    #                     (1, "lime")]
    #     fig = px.imshow(tmp_sim_matrix,
    #                     labels=dict(x=country_1, y=country_2, color="Semantic similarity"),
    #                     x=tmp_periods,
    #                     y=tmp_periods,
    #                     width=800,
    #                     height=700,
    #                     zmin=0,
    #                     zmax=1,
    #                     color_continuous_scale=color_scheme
    #                     )
    #     fig.update_xaxes(side="top")
    #     fig.update_xaxes(
    #         showticklabels=True,
    #         tickmode='linear',
    #         tickfont=dict(
    #             family='Old Standard TT, serif',
    #             size=8,
    #             color='black')
    #     )
    #     fig.update_yaxes(
    #         scaleanchor="x",
    #         scaleratio=1,
    #         showticklabels=True,
    #         tickmode='linear',
    #         tickfont=dict(
    #             family='Old Standard TT, serif',
    #             size=8,
    #             color='black'
    #         )
    #     )
    #     st.plotly_chart(fig)


def main():
    # st.title('Semantic similarity')
    # display_countries_similarity = st.checkbox('Countries similarity')
    # if display_countries_similarity:
    #     menu_countries_similarity()
    # display_2_countries_similarity = st.checkbox('Time periods similarity between 2 countries')
    # if display_2_countries_similarity:
    #     menu_time_period_similarity()
    st.sidebar.title('')


if __name__ == "__main__":
    main()

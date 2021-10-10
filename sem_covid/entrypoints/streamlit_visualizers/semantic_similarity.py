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
from sem_covid.services.store_registry import store_registry
import plotly.express as px

DATE_COLUMN_NAME = 'date'
EMBEDDING_COLUMN_NAME = 'document_embeddings_use'
COUNTRY_COLUMN_NAME = 'country'
PWDB_COLUMN_NAMES = ['pwdb_category', 'pwdb_funding', 'pwdb_type_of_measure',
                     'pwdb_actors', 'pwdb_target_group_l1', 'pwdb_target_group_l2']


def load_data_in_cache():
    if not hasattr(st, 'easy_cache'):
        es_store = store_registry.es_index_store()
        st.easy_cache = dict()
        st.easy_cache['unified_df'] = es_store.get_dataframe(
            index_name=config.UNIFIED_DATASET_ELASTIC_SEARCH_INDEX_NAME)
        st.write('Data cached!')
    return st.easy_cache


app_cache = load_data_in_cache()
unified_df = app_cache['unified_df']


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


def generate_countries_similarity_matrix(pwdb_dataset: pd.DataFrame,
                                         countries: List[str],
                                         number_of_documents: int):
    n = len(countries)
    sim_matrix = np.zeros((n, n))
    for i in range(0, len(countries)):
        sim_matrix[i][i] = 0
        df_x = pd.DataFrame(pwdb_dataset[pwdb_dataset[COUNTRY_COLUMN_NAME] == countries[i]])
        if len(df_x) > 1:
            for j in range(i + 1, len(countries)):
                df_y = pd.DataFrame(pwdb_dataset[pwdb_dataset[COUNTRY_COLUMN_NAME] == countries[j]])
                if len(df_y) > 1:
                    tmp_sim_matrix = cosine_similarity(df_x[EMBEDDING_COLUMN_NAME].values.tolist(),
                                                       df_y[EMBEDDING_COLUMN_NAME].values.tolist())
                    sim_mean = top_k_mean(tmp_sim_matrix[np.triu_indices_from(tmp_sim_matrix, k=1)],
                                          number_of_documents)
                    sim_matrix[i][j] = sim_matrix[j][i] = sim_mean
    return sim_matrix


def generate_2_country_similarity_matrix(dataset_x: pd.DataFrame, dataset_y: pd.DataFrame,
                                         start_date: str, end_date: str, periods: int,
                                         number_of_documents: int
                                         ):
    dataset_x[DATE_COLUMN_NAME] = pd.to_datetime(dataset_x[DATE_COLUMN_NAME]).dt.date
    dataset_y[DATE_COLUMN_NAME] = pd.to_datetime(dataset_y[DATE_COLUMN_NAME]).dt.date
    time_periods = pd.date_range(start=start_date,
                                 end=end_date,
                                 periods=periods).to_pydatetime().tolist()
    time_periods = list(map(lambda x: x.date(), time_periods))
    time_periods = list(zip(time_periods, time_periods[1:]))
    n = len(time_periods)
    sim_matrix = np.zeros((n, n))
    for i in range(0, n):
        start_y, end_y = time_periods[i]
        tmp_df_y = dataset_y[(dataset_y[DATE_COLUMN_NAME] >= start_y) & (dataset_y[DATE_COLUMN_NAME] < end_y)]
        if len(tmp_df_y):
            for j in range(0, n):
                start_x, end_x = time_periods[j]
                tmp_df_x = dataset_x[(dataset_x[DATE_COLUMN_NAME] >= start_x) & (dataset_x[DATE_COLUMN_NAME] < end_x)]
                if len(tmp_df_x):
                    tmp_sim_matrix = cosine_similarity(tmp_df_x[EMBEDDING_COLUMN_NAME].values.tolist(),
                                                       tmp_df_y[EMBEDDING_COLUMN_NAME].values.tolist())
                    sim_mean = top_k_mean(tmp_sim_matrix[np.triu_indices_from(tmp_sim_matrix, k=1)],
                                          number_of_documents)
                    sim_matrix[i][j] = sim_mean
    return sim_matrix, time_periods


def plot_sim_histogram(dataset: pd.DataFrame,
                       dataset_name_x: str,
                       dataset_name_y: str,
                       bins_step: float
                       ):
    dataset_x = pd.DataFrame(dataset[dataset.doc_source == dataset_name_x].copy())
    dataset_y = pd.DataFrame(dataset[dataset.doc_source == dataset_name_y].copy())
    tmp_sim_array = cosine_similarity(dataset_x[EMBEDDING_COLUMN_NAME].values.tolist(),
                                      dataset_y[EMBEDDING_COLUMN_NAME].values.tolist())
    tmp_sim_array.sort()
    counts, bins = np.histogram(tmp_sim_array,
                                bins=np.arange(-1, 1, bins_step))
    counts = counts / tmp_sim_array.size
    bins = 0.5 * (bins[:-1] + bins[1:])
    fig = px.bar(x=bins, y=counts,
                 labels={'x': f'similarity distribution between {dataset_name_x} and {dataset_name_y} ',
                         'y': 'count'})
    st.plotly_chart(fig)


def time_range_selector(selector_1, selector_2):
    start_date = str(selector_1.date_input('start date', value=datetime(2020, 1, 1),
                                           min_value=datetime(2020, 1, 1),
                                           max_value=datetime(2021, 6, 1)))
    end_date = str(selector_2.date_input('end date', value=datetime(2021, 6, 1),
                                         min_value=datetime(2020, 1, 1),
                                         max_value=datetime(2021, 6, 1)))
    return start_date, end_date


def dataset_filter(dataset: pd.DataFrame, time_range_filter: bool = True) -> pd.DataFrame:
    use_filters = st.checkbox('Use filters')
    result_dataset = pd.DataFrame(dataset.copy())
    if use_filters:
        column_options = {
            pwdb_column_name: list(unique_everseen(dataset[pwdb_column_name].explode().dropna().values))
            for pwdb_column_name in PWDB_COLUMN_NAMES
        }
        col1, col2 = st.columns(2)
        selected_column = col1.selectbox('Filter by column', list(column_options.keys()))

        selected_column_value = col2.selectbox(selected_column, column_options[selected_column])
        tmp_df = dataset[selected_column].explode()
        result_dataset = pd.DataFrame(
            dataset.loc[list(unique_everseen(tmp_df[tmp_df == selected_column_value].index))].copy())
        if time_range_filter:
            col3, col4 = st.columns(2)
            start_date, end_date = time_range_selector(col3, col4)
            result_dataset = result_dataset[(result_dataset[DATE_COLUMN_NAME] >= start_date) &
                                            (result_dataset[DATE_COLUMN_NAME] <= end_date)]

    return result_dataset


def menu_countries_similarity():
    number_of_docs = st.slider('Number of documents', min_value=1, max_value=50, step=1, value=10)
    all_datasets = st.checkbox('All datasets')
    if all_datasets:
        dataset = unified_df
    else:
        dataset = unified_df[unified_df.doc_source == 'ds_pwdb']
    countries = list(unique_everseen(dataset.country.values))

    dataset = dataset_filter(dataset)

    if st.button('Generate plot'):
        countries_similarity_matrix = generate_countries_similarity_matrix(pwdb_dataset=dataset,
                                                                           countries=countries,
                                                                           number_of_documents=number_of_docs
                                                                           )
        fig = px.imshow(countries_similarity_matrix,
                        labels=dict(color="Semantic similarity"),
                        x=countries,
                        y=countries,
                        width=700,
                        height=700
                        )
        fig.update_xaxes(side="top")
        st.plotly_chart(fig)


def menu_time_period_similarity():
    col1, col2, col3, col4 = st.columns(4)
    dataset = unified_df
    countries = list(unique_everseen(dataset[COUNTRY_COLUMN_NAME].values))
    country_1 = col1.selectbox('First country', countries)
    country_2 = col2.selectbox('Second country', countries)
    dataset = dataset_filter(dataset, time_range_filter=False)
    start_date, end_date = time_range_selector(col3, col4)
    number_of_periods = st.slider('Periods', min_value=1, max_value=12, step=1, value=6)
    number_of_docs = st.slider('Number of documents', min_value=1, max_value=50, step=1, value=10)
    if st.button('Generate plot'):
        df_x = pd.DataFrame(dataset[dataset[COUNTRY_COLUMN_NAME] == country_1].copy())
        df_y = pd.DataFrame(dataset[dataset[COUNTRY_COLUMN_NAME] == country_2].copy())
        tmp_sim_matrix, tmp_periods = generate_2_country_similarity_matrix(df_x, df_y, start_date=start_date,
                                                                           end_date=end_date, periods=number_of_periods,
                                                                           number_of_documents=number_of_docs
                                                                           )
        tmp_periods = [' '.join([str(x), str(y)]) for x, y in tmp_periods]
        color_scheme = [(0, "orange"),
                        (0.5, "yellow"),
                        (1, "lime")]
        fig = px.imshow(tmp_sim_matrix,
                        labels=dict(x=country_1, y=country_2, color="Semantic similarity"),
                        x=tmp_periods,
                        y=tmp_periods,
                        width=800,
                        height=700,
                        zmin=0,
                        zmax=1,
                        color_continuous_scale=color_scheme
                        )
        fig.update_xaxes(side="top")
        fig.update_xaxes(
            showticklabels=True,
            tickmode='linear',
            tickfont=dict(
                family='Old Standard TT, serif',
                size=8,
                color='black')
        )
        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
            showticklabels=True,
            tickmode='linear',
            tickfont=dict(
                family='Old Standard TT, serif',
                size=8,
                color='black'
            )
        )
        st.plotly_chart(fig)


def menu_sm_histogram():
    st.write('Semantic similarity histogram')
    doc_sources = list(unique_everseen(unified_df.doc_source.values))
    col1, col2 = st.columns(2)
    dataset_name_x = col1.selectbox('Dataset name X', doc_sources)
    dataset_name_y = col2.selectbox('Dataset name Y', doc_sources)
    bins_step = st.slider('Bins step', min_value=0.01, max_value=0.25, step=0.01, value=0.05)
    dataset = unified_df
    dataset = dataset_filter(dataset)
    if st.button('Generate plot'):
        plot_sim_histogram(dataset, dataset_name_x, dataset_name_y, bins_step)


def foo_calc(dataset: pd.DataFrame,
             group_by: str,
             column_values: List[str],
             filter_field: str,
             top_k: int
             ):
    tmp_df = {}
    for column_value in column_values:
        df_x = pd.DataFrame(dataset[dataset[group_by] == column_value])
        tmp_df[column_value] = df_x[filter_field].explode().value_counts(normalize=True).nlargest(top_k)
    return tmp_df


def menu_pwdb_columns_differ():
    dataset = unified_df
    radio1, radio2, radio3 = st.columns(3)
    group_by = radio1.radio('Select group by:', ['country', 'doc_source'])
    analyze_type = radio2.radio('Analyze:', ['pair', 'all'])
    differ_type = radio3.radio('Differ type:', ['common', 'uncommon', 'all'])
    analyze_columns = list(unique_everseen(unified_df[group_by].values))
    if analyze_type == 'pair':
        col1, col2 = st.columns(2)
        name_x = col1.selectbox('Name X', analyze_columns)
        name_y = col2.selectbox('Name Y', analyze_columns)
        analyze_columns = [name_x, name_y]
    pwdb_column = st.selectbox('PWDB Column', PWDB_COLUMN_NAMES)
    top_k = st.slider('Top K column value', min_value=1, max_value=15, step=1, value=5)

    if st.button('Generate plot'):
        plot_df = pd.DataFrame(foo_calc(dataset, group_by, analyze_columns, pwdb_column, top_k)).T
        result_columns = plot_df.columns
        if differ_type != 'all':
            common_columns = plot_df.dropna(axis=1).columns
            differ_columns = [column for column in plot_df.columns if column not in common_columns]
            result_columns = common_columns if differ_type == 'common' else differ_columns
        if len(result_columns) > 1:
            fig = px.bar(plot_df, x=plot_df.index, y=result_columns,
                         barmode='group',
                         height=800, width=800, )
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="left",
                x=0
            ))
            st.plotly_chart(fig)
        else:
            st.write('No data')


def menu_pwdb_columns_evolution():
    col1, col2, col3, col4 = st.columns(4)
    dataset_name = col1.selectbox('Dataset name', list(unique_everseen(unified_df.doc_source)) + ['all'])
    pwdb_column_name = col2.selectbox('PWDB column name', PWDB_COLUMN_NAMES)
    start_date, end_date = time_range_selector(col3, col4)
    normalized_result = st.checkbox('Normalize')
    if st.button('Generate plot'):

        dataset = unified_df[unified_df.doc_source == dataset_name] if dataset_name != 'all' else unified_df
        dataset = pd.DataFrame(dataset.copy())
        dataset.date = pd.to_datetime(dataset.date).dt.date

        dates = dataset.date.unique()

        result_df = {}
        for date in dates:
            result_df[date] = dataset[dataset.date == date][pwdb_column_name].explode().value_counts(
                normalize=normalized_result)
        time_plot_df = pd.DataFrame(result_df).T

        time_plot_df.sort_index(inplace=True)

        fig = px.line(time_plot_df, x=time_plot_df.index, y=time_plot_df.columns,
                      range_x=[start_date, end_date],
                      height=600, width=800,
                      )
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.20,
            xanchor="left",
            x=0
        )
        )
        fig.update_traces(connectgaps=True,
                          fill='tozeroy')
        st.plotly_chart(fig)


def main():
    navigation_pages = {
        'Semantic similarity for all countries': menu_countries_similarity,
        'Semantic similarity in time': menu_time_period_similarity,
        'Semantic similarity between datasets': menu_sm_histogram,
        'PWDB columns differ': menu_pwdb_columns_differ,
        'PWDB columns evolution over time': menu_pwdb_columns_evolution,
    }

    st.sidebar.title('Navigation')
    selected_page = st.sidebar.radio('Go to', list(navigation_pages.keys()))
    next_page = navigation_pages[selected_page]
    next_page()


if __name__ == "__main__":
    main()

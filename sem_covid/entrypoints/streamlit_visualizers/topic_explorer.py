#!/usr/bin/python3

# topic_explorer.py
# Date:  22.10.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
import itertools
from datetime import datetime
from typing import Any, List

import streamlit as st
import pandas as pd
from more_itertools import unique_everseen
import numpy as np
from numpy import mean
from plotly.subplots import make_subplots
from sklearn.metrics.pairwise import cosine_similarity

from sem_covid import config
from sem_covid.services.store_registry import store_registry
import plotly.express as px
import mlflow
import plotly.graph_objects as go
from collections import Counter

CONTENT_CLEANED_TOPIC_MODELING_COLUMN_NAME = 'content_cleaned_topic_modeling'
DOCUMENT_EMBEDDINGS_EURLEX_BERT_COLUMN_NAME = 'document_embeddings_eurlex_bert'
COUNTRY_COLUMN_NAME = 'country'
DOC_SOURCE = 'doc_source'
PWDB_ACTORS = 'pwdb_actors'
EU_CELLAR_AUTHOR_LABELS = 'eu_cellar_author_labels'
DATE_COLUMN_NAME = 'date'
EMBEDDING_COLUMN_NAME = 'document_embeddings_use'
COUNTRY_COLUMN_NAME = 'country'
PWDB_COLUMN_NAMES = ['pwdb_category', 'pwdb_funding', 'pwdb_type_of_measure',
                     'pwdb_actors', 'pwdb_target_group_l1', 'pwdb_target_group_l2']

COLORS = ['#001a33', '#cc0000', '#0072B2', '#996666', '#CC79A7', '#ff3333',
          '#00b300', '#ffff00', '#4d004d', '#99ccff', '#0073e6', '#b3b300']

EXPERIMENT_ID = '120'
BUCKET_NAME = 'mlflow'


def load_data_in_cache():
    if not hasattr(st, 'easy_cache'):
        es_store = store_registry.es_index_store()
        st.easy_cache = dict()
        ds_unified = es_store.get_dataframe(
            index_name=config.UNIFIED_DATASET_ELASTIC_SEARCH_INDEX_NAME)
        all_runs = mlflow.search_runs(
            experiment_ids=EXPERIMENT_ID
        )
        all_runs['params.freq_topic_minus_1'] = all_runs['params.freq_topic_minus_1'].astype('int')
        all_runs.sort_values(by='params.freq_topic_minus_1', ascending=True, inplace=True)
        best_run = all_runs.iloc[0]
        topic_model = store_registry.minio_feature_store(BUCKET_NAME).get_features(
            features_name=f'{EXPERIMENT_ID}/{best_run.run_id}/artifacts/model/model.pkl')
        _, probabilities = topic_model.transform(documents=ds_unified[CONTENT_CLEANED_TOPIC_MODELING_COLUMN_NAME],
                                                 embeddings=np.array(
                                                     list(ds_unified[DOCUMENT_EMBEDDINGS_EURLEX_BERT_COLUMN_NAME])))
        ds_unified['probabilities'] = list(probabilities)
        ds_unified['topic'] = ds_unified['probabilities'].apply(lambda x: np.argmax(x))
        st.easy_cache['topic_model'] = topic_model
        st.easy_cache['unified_df'] = ds_unified
        st.write('Data cached!')
    return st.easy_cache


app_cache = load_data_in_cache()
unified_df = app_cache['unified_df']
topic_model = app_cache['topic_model']


def get_topic_label(topic):
    words = topic_model.get_topic(topic)
    label = [word[0] for word in words[:5]]
    label = f"<b>Topic {topic}</b>: {'_'.join(label)}"
    label = label[:50] + "..." if len(label) > 50 else label

    return label


def get_top_k_topics(topics, k):
    topics_counter = Counter(topics)
    top_k_topics = [x[0] for x in topics_counter.most_common(k)]

    return top_k_topics


def time_range_selector(selector_1, selector_2):
    start_date = str(selector_1.date_input('start date', value=datetime(2020, 1, 1),
                                           min_value=datetime(2020, 1, 1),
                                           max_value=datetime(2021, 6, 1)))
    end_date = str(selector_2.date_input('end date', value=datetime(2021, 6, 1),
                                         min_value=datetime(2020, 1, 1),
                                         max_value=datetime(2021, 6, 1)))
    return start_date, end_date


def dataset_source_filter(dataset: pd.DataFrame) -> pd.DataFrame:
    doc_sources = list(unique_everseen(unified_df.doc_source.values))
    dataset_name = st.selectbox('Dataset name', doc_sources)
    dataset = pd.DataFrame(dataset[dataset.doc_source == dataset_name].copy())
    return dataset


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


def dataset_multi_filter(dataset: pd.DataFrame, time_range_filter: bool = True,
                         is_optional_filter: bool = True) -> tuple:
    use_filters = not is_optional_filter
    if is_optional_filter:
        use_filters = st.checkbox('Use filters')
    result_dataset = pd.DataFrame(dataset.copy())
    selected_column = ""
    selected_column_values = []
    if use_filters:
        column_options = {
            pwdb_column_name: list(unique_everseen(dataset[pwdb_column_name].explode().dropna().values))
            for pwdb_column_name in PWDB_COLUMN_NAMES
        }
        col1, col2 = st.columns(2)
        selected_column = col1.selectbox('Filter by column', list(column_options.keys()))

        selected_column_values = col2.multiselect(selected_column, column_options[selected_column])
        tmp_df = dataset[selected_column].explode()
        result_dataset = pd.DataFrame(
            dataset.loc[list(unique_everseen(tmp_df.isin(selected_column_values).index))].copy())
        if time_range_filter:
            col3, col4 = st.columns(2)
            start_date, end_date = time_range_selector(col3, col4)
            result_dataset = result_dataset[(result_dataset[DATE_COLUMN_NAME] >= start_date) &
                                            (result_dataset[DATE_COLUMN_NAME] <= end_date)]

    return result_dataset, selected_column, selected_column_values


def visualize_evolution_of_topics(dataset, k):
    data_filtered_by_col_val = dataset

    top_k_topics = get_top_k_topics(data_filtered_by_col_val['topic'], k)

    data_filtered_by_col_val = data_filtered_by_col_val.loc[data_filtered_by_col_val['topic'].isin(top_k_topics), :]
    data_filtered_by_col_val['date'] = data_filtered_by_col_val['date'].apply(lambda x: '-'.join(x.split('-')[:2]))
    data_filtered_by_col_val['topic_frequency'] = 1
    data_filtered_by_col_val = data_filtered_by_col_val.groupby(['date', 'topic'])[
        'topic_frequency'].size().reset_index(name='frequency')
    data_filtered_by_col_val['top_n_words'] = data_filtered_by_col_val['topic'].apply(
        lambda t: ', '.join([row[0] for row in topic_model.get_topic(t)]))

    fig = go.Figure()

    for index, topic in enumerate(top_k_topics):
        trace_data = data_filtered_by_col_val.loc[data_filtered_by_col_val['topic'] == topic, :]
        topic_label = get_topic_label(topic)
        words = trace_data['top_n_words']

        fig.add_trace(go.Scatter(x=trace_data['date'],
                                 y=trace_data['frequency'],
                                 mode='lines+markers',
                                 marker_color=COLORS[index],
                                 showlegend=True,
                                 name=topic_label,
                                 hoverinfo='text',
                                 hovertext=[f'<b>Topic {topic}</b><br>Words: {word}' for word in words]))

    fig.update_layout(
        yaxis_title='Frequency',
        title={'text': '<b>Topics over Time',
               'y': .95,
               'x': 0.40,
               'xanchor': 'center',
               'yanchor': 'top',
               'font': dict(size=22, color='Black')
               },
        template='simple_white',
        width=1250,
        height=450,
        hoverlabel=dict(bgcolor='white', font_size=16, font_family='Rockwell'),
        legend=dict(title='<b>Topic Representation')
    )

    fig.update_xaxes(
        showgrid=True
    )

    fig.update_yaxes(
        showgrid=True
    )

    return fig


def menu_topics_over_time():
    data = unified_df.copy()
    number_of_topics = st.slider('Number of topics', min_value=1, max_value=10, step=1, value=1)
    data_filtered = dataset_filter(data)
    if st.button('Generate plot'):
        fig = visualize_evolution_of_topics(data_filtered, number_of_topics)
        st.plotly_chart(fig)


def menu_topics_exploration():
    topic_visualisations = {'Default': lambda: topic_model.visualize_topics(top_n_topics=10, width=800, height=800),
                            'BarChart': lambda: topic_model.visualize_barchart(top_n_topics=10, n_words=5, width=800,
                                                                               height=800),
                            'Hierarchy': lambda: topic_model.visualize_hierarchy(top_n_topics=10, width=800, height=800)
                            }
    selected_type_plot = st.selectbox('Select topic visualisation', topic_visualisations.keys())
    if st.button('Generate plot'):
        fig = topic_visualisations[selected_type_plot]()
        st.plotly_chart(fig)


def menu_non_temporal_comparison_of_country_pairs():
    pass


def visualize_topic_intersection_matrix(dataset, first_country, second_country, k):
    data = dataset.copy()

    topics_first_country = data[data[COUNTRY_COLUMN_NAME] == first_country]['topic']
    topics_second_country = data[data[COUNTRY_COLUMN_NAME] == second_country]['topic']

    topics_x = get_top_k_topics(topics_first_country, k)
    topics_y = get_top_k_topics(topics_second_country, k)

    nr_of_rows = len(topics_y)  # rows correspond to y-axis
    nr_of_cols = len(topics_x)  # columns correspond to x-axis

    intersection_matrix = np.zeros((nr_of_rows, nr_of_cols))

    for i, topic in enumerate(topics_y):
        if topic in topics_x:
            j = topics_x.index(topic)
            intersection_matrix[i, j] = 1

    fig = px.imshow(intersection_matrix,
                    labels=dict(
                        x=first_country,
                        y=second_country,
                        color='Same topic'
                    ),
                    x=[get_topic_label(t) for t in topics_x],
                    y=[get_topic_label(t) for t in topics_y],
                    color_continuous_scale=[(0.00, 'rgb(230, 242, 255)'), (0.50, 'rgb(230, 242, 255)'),
                                            (0.50, 'rgb(0, 0, 102)'), (1, 'rgb(0, 0, 102)')]
                    )

    fig.update_layout(
        width=900,
        height=700,
        coloraxis_colorbar=dict(
            title=f'<b>Intersection of topics',
            tickvals=[0.25, 0.75],
            ticktext=['No', 'Yes'],
            len=0.25
        )
    )

    fig.update_xaxes(
        side='top',
        tickmode='linear'
    )

    fig.update_yaxes(
        tickmode='linear'
    )

    return fig


def menu_topic_intersection():
    dataset = unified_df.copy()
    col1, col2, col3 = st.columns(3)
    countries = list(unique_everseen(dataset[COUNTRY_COLUMN_NAME].values))
    country_x = col1.selectbox('Country X', countries)
    country_y = col2.selectbox('Country Y', countries)
    number_of_topics = col3.slider('Number of topics', min_value=1, max_value=10, step=1, value=5)
    dataset = dataset_filter(dataset)
    if st.button('Generate plot'):
        fig = visualize_topic_intersection_matrix(dataset,
                                                  country_x,
                                                  country_y,
                                                  k=number_of_topics)
        st.plotly_chart(fig)


def visualize_topic_difference_matrix(dataset, first_country, second_country, k):
    data = dataset.copy()

    topics_first_country = data[data[COUNTRY_COLUMN_NAME] == first_country]['topic']
    topics_second_country = data[data[COUNTRY_COLUMN_NAME] == second_country]['topic']

    top_k_topics_first_country = get_top_k_topics(topics_first_country, k)
    top_k_topics_second_country = get_top_k_topics(topics_second_country, k)

    topics_x = list(set(top_k_topics_first_country) - set(top_k_topics_second_country))
    topics_y = list(set(top_k_topics_second_country) - set(top_k_topics_first_country))

    nr_of_rows = len(topics_y)  # rows correspond to y-axis
    nr_of_cols = len(topics_x)  # columns correspond to x-axis

    diff_matrix = np.zeros((nr_of_rows, nr_of_cols))

    indices_upper_triangle = np.triu_indices_from(diff_matrix, 1)
    indices_lower_triangle = np.tril_indices_from(diff_matrix, -1)

    diff_matrix[indices_upper_triangle] = 1
    diff_matrix[indices_lower_triangle] = -1

    fig = px.imshow(diff_matrix,
                    labels=dict(
                        x=first_country,
                        y=second_country
                    ),
                    x=[get_topic_label(t) for t in topics_x],
                    y=[get_topic_label(t) for t in topics_y],
                    color_continuous_scale=[(0.00, 'rgb(255, 255, 30)'), (0.33, 'rgb(255, 255, 30)'),
                                            (0.33, 'rgb(0, 0, 150)'), (0.66, 'rgb(0, 0, 150)'),
                                            (0.66, 'rgb(150, 210, 255)'), (1, 'rgb(150, 210, 255)')]
                    )

    fig.update_layout(
        width=900,
        height=700,
        coloraxis_colorbar=dict(
            tickvals=[-0.66, 0, 0.66],
            ticktext=['Topic present in second country',
                      'Principal diagonal',
                      'Topic present in first country'],
            len=0.25
        )
    )

    fig.update_xaxes(
        side='top',
        tickmode='linear'
    )

    fig.update_yaxes(
        tickmode='linear'
    )

    fig.update_traces(
        hovertemplate=None,
        hoverinfo='skip'
    )

    return fig


def menu_topic_difference():
    dataset = unified_df.copy()
    col1, col2, col3 = st.columns(3)
    countries = list(unique_everseen(dataset[COUNTRY_COLUMN_NAME].values))
    country_x = col1.selectbox('Country X', countries)
    country_y = col2.selectbox('Country Y', countries)
    number_of_topics = col3.slider('Number of topics', min_value=1, max_value=10, step=1, value=5)
    dataset = dataset_filter(dataset)
    if st.button('Generate plot'):
        fig = visualize_topic_difference_matrix(dataset,
                                                country_x,
                                                country_y,
                                                number_of_topics)
        st.plotly_chart(fig)


def visualize_distribution_of_topics(dataset, column_to_filter_by, column_values):
    fig = make_subplots(rows=len(column_values), shared_xaxes=True)

    data = dataset.copy()
    data['top_5_topics'] = data['probabilities'].apply(lambda x: x.argsort()[-5:][::-1])

    for idx, col_value in enumerate(column_values):
        tmp_df = data[column_to_filter_by].explode()
        data_filtered_by_col_value = pd.DataFrame(
            data.loc[list(unique_everseen(tmp_df[tmp_df == col_value].index))].copy())

        data_filtered_by_col_value.reset_index(drop=True, inplace=True)

        topics = list(itertools.chain.from_iterable(data_filtered_by_col_value['top_5_topics']))
        topics_counter = Counter(topics)
        tc_sorted = {k: v for k, v in sorted(topics_counter.items(), key=lambda item: item[1])[-10:]}

        n = len(data_filtered_by_col_value)
        labels = []
        vals = []

        for itm in tc_sorted.items():
            topic = itm[0]
            label = get_topic_label(topic)
            labels.append(label)

            abs_count = itm[1]
            rel_count = abs_count / n
            vals.append(rel_count)

        fig.add_trace(
            go.Bar(
                x=vals,
                y=labels,
                name=col_value,
                marker_color=COLORS[idx],
                showlegend=True,
                orientation='h'),
            row=idx + 1,
            col=1)

    fig.update_layout(
        width=1250,
        height=625,
        title=dict(
            text='<b>Distribution of topics',
            y=.95,
            x=0.40,
            xanchor='center',
            yanchor='top',
            font=dict(
                size=22,
                color='Black'
            )
        ),
        legend=dict(title=f'<b>{column_to_filter_by.capitalize()}')
    )

    fig.update_xaxes(
        tickfont_size=12
    )

    fig.update_yaxes(
        tickmode='linear',
        tickfont_size=12
    )

    return fig


def menu_topics_distribution():
    dataset = unified_df.copy()
    dataset = dataset_source_filter(dataset)
    dataset, column_filter, column_values = dataset_multi_filter(dataset, is_optional_filter=False)
    if st.button('Generate plot'):
        if column_filter and len(column_values):
            fig = visualize_distribution_of_topics(dataset=dataset,
                                                   column_to_filter_by=column_filter,
                                                   column_values=column_values)
            st.plotly_chart(fig)
        else:
            st.write('Select filter column values!')


def main():
    navigation_pages = {
        'Topics over time [BQ9]': menu_topics_over_time,
        'Topics exploration [BQ4]': menu_topics_exploration,
        #'Non-Temporal comparison of country pairs [BQ8]': menu_non_temporal_comparison_of_country_pairs,
        'Topic intersection matrix for all countries (symmetric matrix) [BQ8]': menu_topic_intersection,
        'Topic difference matrix for all countries (asymmetric matrix) [BQ8]': menu_topic_difference,
        'Topics distribution [BQ1, BQ8]': menu_topics_distribution
    }

    st.sidebar.title('Navigation')
    selected_page = st.sidebar.radio('Go to', list(navigation_pages.keys()))
    next_page = navigation_pages[selected_page]
    next_page()


if __name__ == "__main__":
    main()

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

COLUMN_FILTERS = PWDB_COLUMN_NAMES + [COUNTRY_COLUMN_NAME]

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
    all_datasets = 'All datasets'
    doc_sources = list(unique_everseen(unified_df.doc_source.values)) + [all_datasets]
    dataset_name = st.selectbox('Dataset name', doc_sources)
    if dataset_name == all_datasets:
        dataset = pd.DataFrame(dataset.copy())
    else:
        dataset = pd.DataFrame(dataset[dataset.doc_source == dataset_name].copy())
    return dataset


def dataset_filter(dataset: pd.DataFrame, time_range_filter: bool = True) -> pd.DataFrame:
    use_filters = st.checkbox('Use filters')
    result_dataset = pd.DataFrame(dataset.copy())
    if use_filters:
        column_options = {
            pwdb_column_name: list(unique_everseen(dataset[pwdb_column_name].explode().dropna().values))
            for pwdb_column_name in COLUMN_FILTERS
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
            for pwdb_column_name in COLUMN_FILTERS
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


def visualize_evolution_of_topics(dataset, k, column_value):
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
                                 #marker_color=COLORS[index],
                                 showlegend=True,
                                 name=topic_label,
                                 hoverinfo='text',
                                 hovertext=[f'<b>Topic {topic}</b><br>Words: {word}' for word in words]))

    fig.update_layout(
        yaxis_title='Frequency',
        title={'text': f'<b>Topics over Time for {column_value}',
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
    number_of_topics = st.slider('Number of topics', min_value=1, max_value=20, step=1, value=5)
    data_filtered, column_filter, column_values = dataset_multi_filter(data)
    if st.button('Generate plot'):
        if column_filter:
            for column_value in column_values:
                tmp_df = data_filtered[column_filter].explode()
                tmp_df = pd.DataFrame(
                    data_filtered.loc[list(unique_everseen(tmp_df[tmp_df == column_value].index))].copy())
                fig = visualize_evolution_of_topics(tmp_df, number_of_topics, column_value)
                st.plotly_chart(fig)
        else:
            fig = visualize_evolution_of_topics(data_filtered, number_of_topics, "")
            st.plotly_chart(fig)


def menu_topics_exploration():
    topic_visualisations = {
        'BarChart': lambda n_topics, n_words: topic_model.visualize_barchart(top_n_topics=n_topics, n_words=n_words,
                                                                             width=800,
                                                                             height=800),
        '2D Plot representation ': lambda n_topics, n_words: topic_model.visualize_topics(top_n_topics=n_topics,
                                                                                          width=800,
                                                                                          height=800),
        'Hierarchy': lambda n_topics, n_words: topic_model.visualize_hierarchy(top_n_topics=n_topics, width=800,
                                                                               height=800)
    }
    selected_type_plot = st.selectbox('Select topic visualisation', topic_visualisations.keys())
    number_of_topics = st.slider('Number of topics', min_value=1, max_value=30, step=1, value=5)
    number_of_words = st.slider('Number of words', min_value=1, max_value=30, step=1, value=5)
    if st.button('Generate plot'):
        fig = topic_visualisations[selected_type_plot](number_of_topics, number_of_words)
        st.plotly_chart(fig)


def group_dataframe_rows(dataset: pd.DataFrame,
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


def menu_topics_differ():
    top_k_topics = 5
    dataset = pd.DataFrame(unified_df.copy())
    pwdb_column = 'topic'

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

    top_k = st.slider('Top K topics', min_value=1, max_value=15, step=1, value=5)

    if st.button('Generate plot'):
        plot_df = pd.DataFrame(group_dataframe_rows(dataset, group_by, analyze_columns, pwdb_column, top_k)).T
        plot_df.columns = [get_topic_label(t) for t in plot_df.columns]
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
        height=800,
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
    use_filters = st.checkbox('Use filters')
    if use_filters:
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
    elif st.button('Generate plot'):
        doc_sources = list(unique_everseen(unified_df.doc_source.values))
        fig = visualize_distribution_of_topics(dataset=dataset,
                                               column_to_filter_by=DOC_SOURCE,
                                               column_values=doc_sources)
        st.plotly_chart(fig)


def main():
    navigation_pages = {
        'Topics over time [BQ9]': menu_topics_over_time,
        'Topics exploration [BQ4]': menu_topics_exploration,
        'Topics differ [BQ8]': menu_topics_differ,
        'Topics distribution [BQ1, BQ8]': menu_topics_distribution
    }
    st.sidebar.title('Navigation')
    selected_page = st.sidebar.radio('Go to', list(navigation_pages.keys()))
    next_page = navigation_pages[selected_page]
    next_page()


if __name__ == "__main__":
    main()

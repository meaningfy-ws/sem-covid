#!/usr/bin/python3

# topic_explorer.py
# Date:  22.10.2021
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
import mlflow
import plotly.graph_objects as go
from collections import Counter

CONTENT_CLEANED_TOPIC_MODELING_COLUMN_NAME = 'content_cleaned_topic_modeling'
DOCUMENT_EMBEDDINGS_EURLEX_BERT_COLUMN_NAME = 'document_embeddings_eurlex_bert'
COUNTRY_COLUMN_NAME = 'country'
DOC_SOURCE = 'doc_source'
PWDB_ACTORS = 'pwdb_actors'
EU_CELLAR_AUTHOR_LABELS = 'eu_cellar_author_labels'

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


def visualize_evolution_of_topics(dataset, column_to_filter_by, column_value, column_that_contains_lists, k):
    data = dataset.copy()

    if column_that_contains_lists == True:
        data_filtered_by_col_val = data[data[column_to_filter_by].apply(lambda x: column_value in x)]
    else:
        data_filtered_by_col_val = data[data[column_to_filter_by] == column_value]

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
    fig = visualize_evolution_of_topics(unified_df, COUNTRY_COLUMN_NAME, 'Spain', False, 1)
    st.plotly_chart(fig)


def menu_topics_exploration():
    pass


def menu_non_temporal_comparison_of_country_pairs():
    pass


def menu_topic_intersection():
    pass


def menu_topic_difference():
    pass


def menu_topics_distribution():
    pass


def main():
    navigation_pages = {
        'Topics over time [BQ9]': menu_topics_over_time,
        'Topics exploration [BQ4]': menu_topics_exploration,
        'Non-Temporal comparison of country pairs [BQ8]': menu_non_temporal_comparison_of_country_pairs,
        'Topic intersection matrix for all countries (symmetric matrix) [BQ8]': menu_topic_intersection,
        'Topic difference matrix for all countries (asymmetric matrix) [BQ8]': menu_topic_difference,
        'Topics distribution [BQ1]': menu_topics_distribution
    }

    st.sidebar.title('Navigation')
    selected_page = st.sidebar.radio('Go to', list(navigation_pages.keys()))
    next_page = navigation_pages[selected_page]
    next_page()


if __name__ == "__main__":
    main()

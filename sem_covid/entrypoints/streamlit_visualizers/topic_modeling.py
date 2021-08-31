
import pickle

import streamlit as st
import streamlit.components.v1 as components
import pyLDAvis

from sem_covid.services.store_registry import store_registry

st.set_page_config(layout="wide")


# streamlit components text
STREAMLIT_TITLE = 'Topic Modeling'
SELECT_DATASET_TEXT = 'select dataset'
SELECT_ALGORITHM_TEXT = 'select algorithm'
SELECT_POS_TEXT = 'select visualized part of speech'
BUTTON_NAME = 'Generate'

# minio paths
BUCKET_NAME = 'topic-modeling'

IRISH_DATASET_NAME = 'irish_timeline'
EU_TIMELINE_DATASET_NAME = 'eu_timeline'
PWDB_DATASET_NAME = 'pwdb'
EURLEX_DATASET_NAME = 'eurlex'

LDA_FOLDER_NAME = '/LDA/'

POS_WORD = 'word'
POS_NOUN = 'verb'
POS_VERB = 'noun'

FILE_EXTENSION = '.pkl'
WORD_FILE_NAME = 'word_visualization'
VERB_FILE_NAME = 'verb_visualization'
NOUN_FILE_NAME = 'noun_visualization'
NOUN_PHRASE_FILE_NAME = 'noun_phrase_visualization'


@st.cache
def call_lda_visualizer(dataset_name: str, visualization_file_name: str, file_extension: str = FILE_EXTENSION,
                        folder_name: str = LDA_FOLDER_NAME, bucket_name: str = BUCKET_NAME) -> pyLDAvis:
    """
        Grabs LDA visualizer from MinIO
    """
    return pickle.loads(store_registry.minio_object_store(bucket_name).get_object(
        dataset_name + folder_name + visualization_file_name + file_extension))


st.title(STREAMLIT_TITLE)

dataset = st.selectbox(
    SELECT_DATASET_TEXT,
    (
        IRISH_DATASET_NAME,
        EU_TIMELINE_DATASET_NAME,
        EURLEX_DATASET_NAME,
        PWDB_DATASET_NAME
    )
)

pos = st.selectbox(
    SELECT_POS_TEXT,
    (
        WORD_FILE_NAME,
        VERB_FILE_NAME,
        NOUN_FILE_NAME,
        NOUN_PHRASE_FILE_NAME
    )
)

if st.button(BUTTON_NAME):
    components.html(
        pyLDAvis.prepared_data_to_html(
            call_lda_visualizer(dataset_name=dataset, visualization_file_name=pos)
        ), width=11400, height=760)

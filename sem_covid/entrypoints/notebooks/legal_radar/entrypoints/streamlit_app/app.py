#!/usr/bin/python3

# app.py
# Date:  27.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import faiss
import pickle
import pandas as pd
import streamlit as st

from sem_covid.entrypoints.notebooks.legal_radar.services.split_documents_pipeline import DOCUMENT_ID_SOURCE
from sem_covid.services.store_registry import store_registry
from sem_covid.services.model_registry import embedding_registry
from sem_covid import config
import numpy as np
from more_itertools import unique_everseen

FAISS_BUCKET_NAME = 'faiss-index'
FAISS_INDEX_FINREG_NAME = 'faiss_index_finreg.pkl'
FIN_REG_SPLITTED_ES_INDEX = 'ds_finreg_splitted'
DATES_DOCUMENT = 'dates_document'
HTML_LINKS = 'htmls_to_download'
DEFAULT_SEARCH = """The Semantic Interoperability Community develops solutions to help European public administrations perform seamless and meaningful cross-border and cross-domain data exchanges."""
TEXT_PIECE = 'text_piece'


@st.cache(allow_output_mutation=True)
def load_documents():
    """Read the data from ES."""
    es_store = store_registry.es_index_store()
    df = es_store.get_dataframe(index_name=config.EU_FINREG_CELLAR_ELASTIC_SEARCH_INDEX_NAME)
    df[DATES_DOCUMENT] = pd.to_datetime(df[DATES_DOCUMENT]).dt.date
    return df


@st.cache(allow_output_mutation=True)
def load_splitted_documents():
    """Read the data from ES."""
    es_store = store_registry.es_index_store()
    return es_store.get_dataframe(index_name=FIN_REG_SPLITTED_ES_INDEX)


@st.cache(allow_output_mutation=True)
def load_emb_model():
    return embedding_registry.sent2vec_universal_sent_encoding()


@st.cache(allow_output_mutation=True)
def load_faiss_index():
    """Load and deserialize the Faiss index."""
    minio_store = store_registry.minio_object_store(minio_bucket=FAISS_BUCKET_NAME)
    data = pickle.loads(minio_store.get_object(object_name=FAISS_INDEX_FINREG_NAME))
    return faiss.deserialize_index(data)


def main():
    # Load data and models
    documents = load_documents()
    splitted_documents = load_splitted_documents()
    model = load_emb_model()
    faiss_index = load_faiss_index()

    st.title("Legal Radar - semantic search")

    # User search
    user_input = st.text_area("Search box", DEFAULT_SEARCH)
    return_whole_document = st.checkbox("Result similarity for document parts", )

    # Filters
    st.sidebar.markdown("**Filters**")
    filter_year = st.sidebar.slider("Publication year", 1900, 2021, (1900, 2021), 1)
    content_length = st.sidebar.slider("Content length", 250, 5000, 250, 50)
    num_results = 100
    if return_whole_document:
        num_results = st.sidebar.slider("Number of text parts in sum", 10, 200, 10)

    # Fetch results
    if user_input:
        # Get paper IDs
        embeddings = model.encode(sentences=[user_input])
        D, I = faiss_index.search(np.array(embeddings).astype("float32"), k=num_results)
        document_parts = splitted_documents.iloc[I.flatten().tolist()]
        document_parts['similarity'] = D.flatten().tolist()
        documents_id = list(unique_everseen(
            splitted_documents.iloc[I.flatten().tolist()][DOCUMENT_ID_SOURCE].values))
        frame = documents.loc[documents_id]
        frame = frame[
            (frame[DATES_DOCUMENT].apply(lambda x: x.year >= filter_year[0] if x else False))
            & (frame[DATES_DOCUMENT].apply(lambda x: x.year <= filter_year[1] if x else False))]
        if not frame.empty:
            # Get individual results
            for index, row in frame.iterrows():
                st.write(f"""**{row['title']}**""")
                st.write(f"""**Dates document:**:
                        {row[DATES_DOCUMENT]}""")
                st.write(f"""**CELEX-NUMBER:**
                        {row.celex_numbers[0]}""")
                if not return_whole_document:
                    st.write(f"""**Content:**
                            {row['content'][:content_length]}...""")
                else:
                    document_parts_by_index = document_parts[document_parts[DOCUMENT_ID_SOURCE] == index]
                    for index1, row1 in document_parts_by_index.iterrows():
                        st.write(f"""**Document part:**
                                {row1[TEXT_PIECE]}""")
                        st.write(f"""**Similarity:**
                                {1 / (1 + row1['similarity'])}""")
                st.write(f"""**EurLex link**
                    https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A{row.celex_numbers[0]}""")
                if row[HTML_LINKS]:
                    for html_link in row[HTML_LINKS]:
                        st.write(
                            f"""** HTML download links **:\n {html_link}""")


if __name__ == "__main__":
    main()

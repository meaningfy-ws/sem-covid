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

FAISS_BUCKET_NAME = 'faiss-index'
FAISS_INDEX_FINREG_NAME = 'faiss_index_finreg.pkl'
FIN_REG_SPLITTED_ES_INDEX = 'ds_finreg_splitted'
DATES_DOCUMENT = 'dates_document'


@st.cache
def load_documents():
    """Read the data from ES."""
    es_store = store_registry.es_index_store()
    df = es_store.get_dataframe(index_name=config.EU_FINREG_CELLAR_ELASTIC_SEARCH_INDEX_NAME)
    df[DATES_DOCUMENT] = df[DATES_DOCUMENT].apply(lambda x: x[0] if x else None)
    df[DATES_DOCUMENT] = pd.to_datetime(df[DATES_DOCUMENT]).date()
    return df


@st.cache
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


def vector_search(query, model, index, num_results=10):
    """Tranforms query to vector using a pretrained, sentence-level
    DistilBERT model and finds similar vectors using FAISS.
    Args:
        query (str): User query that should be more than a sentence long.
        model (sentence_transformers.SentenceTransformer.SentenceTransformer)
        index (`numpy.ndarray`): FAISS index that needs to be deserialized.
        num_results (int): Number of results to return.
    Returns:
        D (:obj:`numpy.array` of `float`): Distance between results and query.
        I (:obj:`numpy.array` of `int`): Paper ID of the results.

    """
    vector = model.encode(list(query))
    D, I = index.search(np.array(vector).astype("float32"), k=num_results)
    return D, I


def id2details(df, I, column):
    """Returns the paper titles based on the paper index."""
    return [list(df[df.id == idx][column]) for idx in I[0]]


def main():
    # Load data and models
    documents = load_documents()
    splitted_documents = load_splitted_documents()
    model = load_emb_model()
    faiss_index = load_faiss_index()

    st.title("Legal Radar - semantic search")

    # User search
    user_input = st.text_area("Search box", "covid-19 misinformation and social media")

    # Filters
    st.sidebar.markdown("**Filters**")
    filter_year = st.sidebar.slider("Publication year", 1900, 2021, (1900, 2021), 1)
    content_length = st.sidebar.slider("Content length", 250, 5000, 250, 50)
    num_results = st.sidebar.slider("Number of search results", 10, 200, 10)

    # Fetch results
    if user_input:
        # Get paper IDs
        embeddings = model.encode(sentences=[user_input])
        D, I = faiss_index.search(np.array(embeddings).astype("float32"), k=num_results)
        documents_id = list(set(
            splitted_documents.iloc[I.flatten().tolist()][DOCUMENT_ID_SOURCE].values))
        # Slice data on year
        # frame = data[
        #     (data.year >= filter_year[0])
        #     & (data.year <= filter_year[1])
        #     & (data.citations >= filter_citations)
        #     ]
        frame = documents[
            (documents[DATES_DOCUMENT].apply(lambda x: x.year >= filter_year[0] if x else False))
            & (documents[DATES_DOCUMENT].apply(lambda x: x.year <= filter_year[1] if x else False))].loc[documents_id]
        # Get individual results
        for index, row in frame.iterrows():
            st.write(
                f"""**{row['title']}**  
                **HTML download links**:\n {row['htmls_to_download']}  
                **Dates document**:\n{row['dates_document']}  
                **Content:**\n{row['content'][:content_length]}...
                """
            )
        # for id_ in I.flatten().tolist():
        #     if id_ in set(frame.id):
        #         f = frame[(frame.id == id_)]
        #     else:
        #         continue
        #
        #     st.write(
        #         f"""**{f.iloc[0].original_title}**
        #     **Citations**: {f.iloc[0].citations}
        #     **Publication year**: {f.iloc[0].year}
        #     **Abstract**
        #     {f.iloc[0].abstract}
        #     """
        #     )


if __name__ == "__main__":
    main()
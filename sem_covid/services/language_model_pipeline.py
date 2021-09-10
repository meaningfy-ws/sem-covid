
import pickle
import re
from typing import List, Tuple

import pandas as pd
import spacy
from gensim.models import Word2Vec

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.document_handling_tools import (
    document_atomization_noun_phrases, lemmatize_document)
from sem_covid.services.sc_wrangling.data_cleaning import (clean_text_from_specific_characters, clean_fix_unicode,
                                                           clean_remove_currency_symbols, clean_remove_emails,
                                                           clean_remove_urls, clean_remove_stopwords)
from sem_covid.services.store_registry import store_registry

nlp = spacy.load('en_core_web_sm')
nlp.max_length = 5000000
WINDOW = 5
MIN_COUNT = 1
VECTOR_SIZE = 300
LANGUAGE_MODEL_MINIO_FOLDER = 'word2vec/'
LANGUAGE_MODEL_BUCKET_NAME = 'mdl-language'


def add_space_between_dots_and_commas(text: str):
    return re.sub(r'(?<=[.,])(?=[^\s])', r' ', text)


def apply_cleaning_functions(document_corpus: pd.Series) -> pd.Series:
    """
    This function receives the document and leads through cleaning steps
    Args:
        document_corpus: dataset document corpus

    Returns: clean document corpus
    """
    unused_characters = ["\\r", ">", "\n", "\\", "<", "''", "%", "...", "\'", '"', "(", "\n", "*", "1)", "2)", "3)",
                         "[", "]", "-", "_", "\r", '®', '..']

    new_document_corpus = document_corpus.apply(clean_text_from_specific_characters, characters=unused_characters)
    new_document_corpus = new_document_corpus.apply(clean_fix_unicode)
    new_document_corpus = new_document_corpus.apply(clean_remove_urls)
    new_document_corpus = new_document_corpus.apply(clean_remove_emails)
    new_document_corpus = new_document_corpus.apply(clean_remove_currency_symbols)
    new_document_corpus = new_document_corpus.apply(clean_remove_stopwords)
    new_document_corpus = new_document_corpus.apply(add_space_between_dots_and_commas)

    return new_document_corpus


class LanguageModelPipeline:
    """
        This pipeline executes the steps for word2vec language training.
    """

    def __init__(self, dataset_sources: List[Tuple[pd.DataFrame, List[str]]], language_model_name: str):
        """
            :param dataset_sources: represents the source of the datasets.
        """
        self.dataset_sources = dataset_sources
        self.language_model_name = language_model_name
        self.documents_corpus = pd.Series()
        self.word2vec = None

    def download_datasets(self):
        """
            In this step it will download the dataset and detect selected columns.
            It can be downloaded as many datasets as there are in data source.
        """
        self.dataset_sources = [(dataset_columns, dataset_source)
                                for dataset_source, dataset_columns in self.dataset_sources]

    def extract_textual_data(self):
        """
            After downloading the datasets, the textual data will be found and and concatenated
            with executing of several steps as well. It will fill the NaN values with empty space,
            add a dot at the end of each concatenated column and reset the index.
        """
        self.documents_corpus = pd.concat([dataset[columns]
                                          .fillna(value="")
                                          .agg('. '.join, axis=1)
                                          .reset_index(drop=True)
                                           for columns, dataset in self.dataset_sources
                                           ], ignore_index=True)

    def clean_textual_data(self):
        """
            The next step is data cleaning. In this step the function "apply_cleaning_functions"
            applies the following actions:
                - clean the document from specific characters
                - delete unicode
                - removes emails and URLs and currency symbols
        """
        self.documents_corpus = apply_cleaning_functions(self.documents_corpus)

    def transform_to_spacy_doc(self):
        """
            When the document is clean, is going to be transform into spacy document
        """
        self.documents_corpus = self.documents_corpus.apply(nlp)

    def extract_features(self):
        """
            To extract the parts of speech, below it was defined classes for each token is necessary.
        """
        self.documents_corpus = pd.concat([self.documents_corpus
                                          .apply(document_atomization_noun_phrases)
                                          .apply(lemmatize_document)], ignore_index=True)

        self.documents_corpus = self.documents_corpus.apply(lambda x: list(map(str, x)))

    def model_training(self):
        """
            When the data is prepared it's stored into Word2Vec model.
        """
        self.word2vec = Word2Vec(sentences=self.documents_corpus, window=WINDOW,
                                 min_count=MIN_COUNT, vector_size=VECTOR_SIZE)

    def save_language_model(self):
        """
            Saves trained model in MinIO
        """
        minio = store_registry.minio_object_store(LANGUAGE_MODEL_BUCKET_NAME)
        minio.put_object(LANGUAGE_MODEL_MINIO_FOLDER + self.language_model_name, pickle.dumps(self.word2vec))

    def execute(self):
        """
            The final step is execution, where are stored each step and it will be executed in a row
        """
        self.download_datasets()
        self.extract_textual_data()
        self.clean_textual_data()
        self.transform_to_spacy_doc()
        self.extract_features()
        self.model_training()
        self.save_language_model()

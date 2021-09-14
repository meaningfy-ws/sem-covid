import pickle
import re
from typing import List, Tuple

import pandas as pd
import spacy
from gensim.models import Word2Vec
from gensim.parsing.preprocessing import remove_stopwords

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.document_handling_tools import (
    document_atomization_noun_phrases, lemmatize_document)

from sem_covid.services.store_registry import store_registry

from sem_covid.adapters.embedding_models import BasicSentenceSplitterModel

from nltk.corpus import words
import enchant

en_words = set(words.words())
d = enchant.Dict("en_US")

nlp = spacy.load('en_core_web_sm')
nlp.max_length = 5000000
WINDOW = 5
MIN_COUNT = 1
VECTOR_SIZE = 300
LANGUAGE_MODEL_MINIO_FOLDER = 'word2vec/'
LANGUAGE_MODEL_BUCKET_NAME = 'mdl-language'


def clean_text(text: str) -> str:
    tmp_text = re.sub(' +', ' ', re.sub(r'[^a-zA-Z]', ' ', text)).lower()
    tmp_text = remove_stopwords(tmp_text)
    tmp_words = tmp_text.split(' ')
    tmp_words = [word for word in tmp_words
                 if len(word) > 3 and (word in en_words or d.check(word))]
    if len(tmp_words) > 3:
        return ' '.join(tmp_words)
    else:
        return ''


def apply_cleaning_functions(document_corpus: pd.Series) -> pd.Series:
    """
    This function receives the document and leads through cleaning steps
    Args:
        document_corpus: dataset document corpus

    Returns: clean document corpus
    """
    splitter = BasicSentenceSplitterModel()
    textual_data = '. '.join(document_corpus.values)
    splitted_text = splitter.split(textual_data)
    splitted_long_text = [sent for sent in splitted_text if len(sent) > 10]
    cleaned_text = list(set([sent for sent in list(map(clean_text, splitted_long_text)) if sent]))
    return pd.Series(cleaned_text)


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

#!/usr/bin/python3

# unified_dataset_pipeline.py
# Date:  28.09.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com


import spacy
nlp = spacy.load('en_core_web_sm')

from sem_covid import config
import numpy as np
from langdetect import detect_langs, DetectorFactory

import pandas as pd
from typing import List
from sem_covid.adapters.abstract_store import IndexStoreABC

from sem_covid.adapters.abstract_model import SentenceEmbeddingModelABC, DocumentEmbeddingModelABC

DetectorFactory.seed = 0

TARGET_GROUPS_L1 = ["businesses", "workers", "citizens"]
COMMON_DATASET_COLUMNS = ["title", "content", "content_cleaned_topic_modeling", "date", "doc_source", "country",
                          "pwdb_category", "pwdb_target_group_l1", "pwdb_funding", "pwdb_type_of_measure", "pwdb_actors",
                          "document_embeddings_use", "document_embeddings_eurlex_bert", "topic_embeddings_eurlex_bert"]

SPECIFIC_DATASET_COLUMNS = ["eu_cellar_subject_matter_labels", "eu_cellar_resource_type_labels",
                            "eu_cellar_directory_code_labels",
                            "eu_cellar_author_labels", "pwdb_target_group_l2", "ireland_keyword",
                            "ireland_department_data",
                            "ireland_campaign", "ireland_page_type", "eu_timeline_topic"]

CONTENT_COLUMN_NAME = 'content'
CONTENT_CLEANED_TOPIC_MODELING_COLUMN_NAME = 'content_cleaned_topic_modeling'
TITLE_COLUMN_NAME = 'title'
DATE_COLUMN_NAME = 'date'
DATE_FILTER_COLUMN_NAME = 'date_filter_column'
DOCUMENT_SOURCE_COLUMN_NAME = 'doc_source'
COUNTRY_COLUMN_NAME = 'country'
PWDB_ACTORS_COLUMN_NAME = "pwdb_actors"
DOCUMENT_EMBEDDINGS_USE_COLUMN_NAME = "document_embeddings_use"
DOCUMENT_EMBEDDINGS_EURLEX_BERT_COLUMN_NAME = "document_embeddings_eurlex_bert"
TOPIC_EMBEDDINGS_EURLEX_BERT_COLUMN_NAME = "topic_embeddings_eurlex_bert"

# PWDB CONSTANTS
PWDB_CONTENT_COLUMNS = ['title', 'background_info_description', 'content_of_measure_description',
                        'use_of_measure_description', 'involvement_of_social_partners_description']
PWDB_DOC_SOURCE = 'ds_pwdb'
PWDB_RENAME_COLUMNS_MAPPING = {"category": "pwdb_category", "funding": "pwdb_funding",
                               "type_of_measure": "pwdb_type_of_measure", "actors": "pwdb_actors",
                               "start_date": "date"}
PWDB_SPECIFIC_COLUMNS = {"pwdb_target_group_l2": "target_groups"}

# EU_CELLAR CONSTANTS
EU_CELLAR_CONTENT_COLUMNS = ["title", "content"]
EU_CELLAR_DOC_SOURCE = 'ds_eu_cellar'
EU_CELLAR_COUNTRY_NAME = "European Union"
EU_CELLAR_PWDB_ACTORS = "EU (Council, EC, EP)"
EU_CELLAR_RENAME_COLUMNS_MAPPING = {"category": "pwdb_category", "funding": "pwdb_funding",
                                    "type_of_measure": "pwdb_type_of_measure",
                                    "dates_document": "date"
                                    }
EU_CELLAR_SPECIFIC_COLUMNS = {"eu_cellar_subject_matter_labels": "subject_matter_labels",
                              "eu_cellar_resource_type_labels": "resource_type_labels",
                              "eu_cellar_directory_codes_labels": "directory_codes_labels",
                              "eu_cellar_author_labels": "author_labels"}

# EU_TIMELINE CONSTANTS
EU_TIMELINE_CONTENT_COLUMNS = ["title", "abstract", "detail_content"]
EU_TIMELINE_DOC_SOURCE = 'ds_eu_timeline'
EU_TIMELINE_COUNTRY_NAME = "European Union"
EU_TIMELINE_PWDB_ACTORS = "EU (Council, EC, EP)"
EU_TIMELINE_RENAME_COLUMNS_MAPPING = {"category": "pwdb_category",
                                      "funding": "pwdb_funding",
                                      "type_of_measure": "pwdb_type_of_measure",
                                      }
EU_TIMELINE_SPECIFIC_COLUMNS = {'eu_timeline_topic': 'topics'}

# IRELAND_TIMELINE CONSTANTS
IRELAND_TIMELINE_CONTENT_COLUMNS = ["title", "content"]
IRELAND_TIMELINE_DOC_SOURCE = 'ds_ireland_timeline'
IRELAND_TIMELINE_COUNTRY_NAME = "Ireland"
IRELAND_TIMELINE_PWDB_ACTORS = "National government"
IRELAND_TIMELINE_RENAME_COLUMNS_MAPPING = {"category": "pwdb_category",
                                           "funding": "pwdb_funding",
                                           "type_of_measure": "pwdb_type_of_measure",
                                           "published_date": "date"
                                           }
IRELAND_TIMELINE_SPECIFIC_COLUMNS = {"ireland_keyword": "keyword",
                                     "ireland_department_data": "department_data",
                                     "ireland_campaigns_links": "campaigns_links",
                                     "ireland_page_type": "page_type"}


def make_target_group_l1_column(dataset: pd.DataFrame):
    """
    This function will create the pwdb_target_group_l1 column for a dataset. The value will be the content merged from
    workers,businesses, citizens column values that are first converted from binary to text.
    """
    for col in TARGET_GROUPS_L1:
        dataset[col] = dataset[col].apply(lambda x: col if x == 1 else "")

    dataset["pwdb_target_group_l1"] = dataset[TARGET_GROUPS_L1].apply(lambda row: ' '.join(row.values.astype(str)),
                                                                      axis=1).apply(lambda x: x.split())


def create_new_column_with_defined_value(dataset: pd.DataFrame, column_name: str, value=None, empty_array=False):
    """
    This function create a column in the dataset with a defined value or with an empty list as value
    """
    if empty_array:
        dataset[column_name] = [np.empty(0, dtype=float)] * len(dataset)
    else:
        dataset[column_name] = value


def replace_non_english_content(text):
    """
    This function will check the content from a language stand point. If the text is not in english more then 95% then
    will replace the text with None.
    """
    if text is not None:
        language = detect_langs(text)
        language_details = str(language[0]).split(":")
        if language_details[0] == "en" and float(language_details[1]) > 0.95:
            return text
        else:
            return None


def clean_txt_topic_modeling(raw_txt: str) -> str:
    """
    This function prepares the text for the topic modeling exercise.
    """
    cleansed_tokens = []

    lowered_txt = raw_txt.lower()

    doc = nlp(lowered_txt)

    for token in doc:
        if not (token.is_stop or token.is_punct or token.is_currency or
                token.like_num or token.like_url or token.like_email):
            cleansed_tokens.append(token.lemma_)

    return ' '.join(cleansed_tokens)


class DefaultDatasetStructureTransformer:
    """
    This class will transform a dataset structure
    """

    def __init__(self, dataset: pd.DataFrame,
                 emb_model_1: SentenceEmbeddingModelABC,
                 emb_model_2: DocumentEmbeddingModelABC,
                 topic_model,
                 content_columns: List[str],
                 doc_source: str,
                 rename_columns_mapping: dict,
                 dataset_specific_columns: dict = None,
                 country: str = None,
                 pwdb_actors: str = None
                 ):
        self.dataset = dataset
        self.content_columns = content_columns
        self.doc_source = doc_source
        self.country = country
        self.pwdb_actors = pwdb_actors
        self.dataset_specific_columns = dataset_specific_columns
        self.rename_columns_mapping = rename_columns_mapping
        self.emb_model_1 = emb_model_1
        self.emb_model_2 = emb_model_2
        self.topic_model=topic_model

    def create_columns(self):
        """
        This is creating the necessary columns in the dataset with values
        """
        self.dataset[CONTENT_COLUMN_NAME] = self.dataset[self.content_columns].agg(
            lambda x: " ".join(item if item else "" for item in x),
            axis=1)
        create_new_column_with_defined_value(self.dataset, DOCUMENT_SOURCE_COLUMN_NAME, self.doc_source)
        if self.country:
            create_new_column_with_defined_value(self.dataset, COUNTRY_COLUMN_NAME, self.country)
        if self.pwdb_actors:
            create_new_column_with_defined_value(self.dataset, PWDB_ACTORS_COLUMN_NAME, self.pwdb_actors)
        make_target_group_l1_column(self.dataset)

        self.dataset[DOCUMENT_EMBEDDINGS_USE_COLUMN_NAME] = self.emb_model_1.encode(
            self.dataset[CONTENT_COLUMN_NAME].values)

        self.dataset[CONTENT_CLEANED_TOPIC_MODELING_COLUMN_NAME] = self.dataset[CONTENT_COLUMN_NAME].apply(
            clean_txt_topic_modeling)

        self.dataset[DOCUMENT_EMBEDDINGS_EURLEX_BERT_COLUMN_NAME] = self.emb_model_2.encode(
            self.dataset[CONTENT_CLEANED_TOPIC_MODELING_COLUMN_NAME].values)

        self.dataset[TOPIC_EMBEDDINGS_EURLEX_BERT_COLUMN_NAME] = self.topic_model.transform(
            documents=self.dataset[CONTENT_CLEANED_TOPIC_MODELING_COLUMN_NAME],
            embeddings=np.array(list(self.dataset[DOCUMENT_EMBEDDINGS_EURLEX_BERT_COLUMN_NAME])))[1].tolist()

        for specific_column in SPECIFIC_DATASET_COLUMNS:
            create_new_column_with_defined_value(self.dataset, column_name=specific_column, empty_array=True)

    def replace_values(self):
        """
        This is copying the values from the existing specific columns in the dataset to the new specific columns created
        """
        if self.dataset_specific_columns:
            for new_column_name, column_name in self.dataset_specific_columns.items():
                self.dataset[new_column_name] = self.dataset[column_name]
                self.dataset[new_column_name] = self.dataset[column_name].apply(lambda x: x if x else [])

    def rename_columns(self):
        """
        this is renaming existing columns in the dataset
        """
        self.dataset.rename(columns=self.rename_columns_mapping, inplace=True)

    def execute(self) -> pd.DataFrame:
        self.create_columns()
        self.replace_values()
        self.rename_columns()
        return self.dataset


class UnifiedDatasetPipeline:
    """
    This class is creating a unified dataset by merging other datasets
    """

    def __init__(self, es_store: IndexStoreABC,
                 emb_model_1: SentenceEmbeddingModelABC,
                 emb_model_2: DocumentEmbeddingModelABC,
                 topic_model,
                 ):
        self.unified_dataset = pd.DataFrame()
        self.es_store = es_store
        self.emb_model_1 = emb_model_1
        self.emb_model_2 = emb_model_2
        self.topic_model=topic_model
        self.pwdb_df = pd.DataFrame()
        self.eu_cellar_df = pd.DataFrame()
        self.eu_timeline_df = pd.DataFrame()
        self.ir_timeline_df = pd.DataFrame()

    def get_steps(self) -> list:
        return [self.extract, self.transform, self.load]

    def extract(self):
        """
        This is getting the datasets from elastic search
        """
        self.pwdb_df = self.es_store.get_dataframe(index_name=config.PWDB_ELASTIC_SEARCH_INDEX_NAME)
        self.eu_cellar_df = self.es_store.get_dataframe(
            index_name=config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME + "_enriched")
        self.eu_timeline_df = self.es_store.get_dataframe(
            index_name=config.EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME + "_enriched")
        self.ir_timeline_df = self.es_store.get_dataframe(
            index_name=config.IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME + "_enriched")

    def transform(self):
        """
        This is transforming the datasets to meet the merging requirements and creates the unified dataset
        """
        self.pwdb_df = DefaultDatasetStructureTransformer(
            dataset=self.pwdb_df,
            emb_model_1=self.emb_model_1,
            emb_model_2=self.emb_model_2,
            topic_model=self.topic_model,
            content_columns=PWDB_CONTENT_COLUMNS,
            doc_source=PWDB_DOC_SOURCE,
            rename_columns_mapping=PWDB_RENAME_COLUMNS_MAPPING,
            dataset_specific_columns=PWDB_SPECIFIC_COLUMNS
        ).execute()
        self.eu_cellar_df = DefaultDatasetStructureTransformer(
            dataset=self.eu_cellar_df,
            emb_model_1=self.emb_model_1,
            emb_model_2=self.emb_model_2,
            topic_model=self.topic_model,
            content_columns=EU_CELLAR_CONTENT_COLUMNS,
            doc_source=EU_CELLAR_DOC_SOURCE,
            rename_columns_mapping=EU_CELLAR_RENAME_COLUMNS_MAPPING,
            dataset_specific_columns=EU_CELLAR_SPECIFIC_COLUMNS,
            country=EU_CELLAR_COUNTRY_NAME,
            pwdb_actors=EU_CELLAR_PWDB_ACTORS
        ).execute()
        self.eu_timeline_df = DefaultDatasetStructureTransformer(
            dataset=self.eu_timeline_df,
            emb_model_1=self.emb_model_1,
            emb_model_2=self.emb_model_2,
            topic_model=self.topic_model,
            content_columns=EU_TIMELINE_CONTENT_COLUMNS,
            doc_source=EU_TIMELINE_DOC_SOURCE,
            rename_columns_mapping=EU_TIMELINE_RENAME_COLUMNS_MAPPING,
            dataset_specific_columns=EU_TIMELINE_SPECIFIC_COLUMNS,
            country=EU_TIMELINE_COUNTRY_NAME,
            pwdb_actors=EU_TIMELINE_PWDB_ACTORS
        ).execute()
        self.ir_timeline_df = DefaultDatasetStructureTransformer(
            dataset=self.ir_timeline_df,
            emb_model_1=self.emb_model_1,
            emb_model_2=self.emb_model_2,
            topic_model=self.topic_model,
            content_columns=IRELAND_TIMELINE_CONTENT_COLUMNS,
            doc_source=IRELAND_TIMELINE_DOC_SOURCE,
            rename_columns_mapping=IRELAND_TIMELINE_RENAME_COLUMNS_MAPPING,
            dataset_specific_columns=IRELAND_TIMELINE_SPECIFIC_COLUMNS,
            country=IRELAND_TIMELINE_COUNTRY_NAME,
            pwdb_actors=IRELAND_TIMELINE_PWDB_ACTORS
        ).execute()
        data_frames = [pd.DataFrame(data_frame[COMMON_DATASET_COLUMNS + SPECIFIC_DATASET_COLUMNS].copy())
                       for data_frame in [self.pwdb_df, self.eu_cellar_df, self.eu_timeline_df, self.ir_timeline_df]]
        for data_frame in data_frames:
            data_frame.columns = COMMON_DATASET_COLUMNS + SPECIFIC_DATASET_COLUMNS
            data_frame[CONTENT_COLUMN_NAME] = data_frame[CONTENT_COLUMN_NAME].apply(
                lambda x: x if x not in ["", " "] else None)
            data_frame[CONTENT_COLUMN_NAME] = data_frame[CONTENT_COLUMN_NAME].apply(
                lambda x: replace_non_english_content(x))
            data_frame.dropna(subset=[CONTENT_COLUMN_NAME, TITLE_COLUMN_NAME, DATE_COLUMN_NAME], how="any",
                              inplace=True)
        self.unified_dataset = pd.DataFrame(pd.concat(data_frames))
        self.unified_dataset.pwdb_funding = self.unified_dataset.pwdb_funding.apply(
            lambda x: x.split('|') if type(x) == str else x)
        self.unified_dataset.pwdb_actors = self.unified_dataset.pwdb_actors.apply(
            lambda x: x if type(x) == list else [x])
        # Note:the index is reset because enriched datasets have numeric indexing
        self.unified_dataset.reset_index(inplace=True, drop=True)

        self.unified_dataset[DATE_FILTER_COLUMN_NAME] = pd.to_datetime(self.unified_dataset[DATE_COLUMN_NAME])
        self.unified_dataset = self.unified_dataset[
            self.unified_dataset[DATE_FILTER_COLUMN_NAME] > pd.to_datetime("2020-01-01")].copy()
        self.unified_dataset.drop(DATE_FILTER_COLUMN_NAME, axis=1, inplace=True)


    def load(self):
        """
        this will put the created unified dataset into elastic search
        """
        self.es_store.put_dataframe(index_name=config.UNIFIED_DATASET_ELASTIC_SEARCH_INDEX_NAME,
                                    content=self.unified_dataset)

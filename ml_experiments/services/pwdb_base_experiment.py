#!/usr/bin/python3

# pwdb_base_experiment.py
# Date:  22/03/2021
# Author: Chiriac Dan
# Email: dan.chiriac1453@gmail.com

"""
    This module deals with the PWDB ML experiment specificities.
"""

import json
import logging
import pickle
from abc import ABC

import pandas as pd
from gensim.models import Word2Vec
from sklearn import model_selection

from ml_experiments.config import config
from ml_experiments.services.base_experiment import BaseExperiment
from ml_experiments.services.sc_wrangling import data_cleaning
from ml_experiments.services.sc_wrangling import feature_selector
from ml_experiments.services.sc_wrangling import pwdb_transformer
from ml_experiments.services.sc_wrangling import value_replacement

logger = logging.getLogger(__name__)

BUSINESSES = [
    'Companies providing essential services', 'Contractors of a company',
    'Larger corporations', 'One person or microenterprises', 'Other businesses',
    'SMEs', 'Sector specific set of companies', 'Solo-self-employed', 'Start-ups']

CITIZENS = [
    'Children (minors)', 'Disabled', 'Migrants', 'Older citizens',
    'Other groups of citizens', 'Parents', 'People in care facilities', 'Refugees',
    'Single parents', 'The COVID-19 risk group', 'Women', 'Youth (18-25)']

WORKERS = [
    'Cross-border commuters', 'Disabled workers', 'Employees in standard employment',
    'Female workers', 'Migrants in employment', 'Older people in employment (aged 55+)',
    'Other groups of workers', 'Parents in employment', 'Particular professions',
    'Platform workers', 'Posted workers', 'Refugees in employment', 'Seasonal workers',
    'Self-employed', 'Single parents in employment', 'The COVID-19 risk group at the workplace',
    'Undeclared workers', 'Unemployed', 'Workers in care facilities',
    'Workers in essential services', 'Workers in non-standard forms of employment',
    'Youth (18-25) in employment']


class PWDBBaseExperiment(BaseExperiment, ABC):
    """
        Base class for all experiments performed on PWDB dataset.The common part to all ML experiments
        is tha data loading, extraction and preparation.

        This is an abstract class that implements only the data preparation steps, common to all ML experiment.
    """

    def __init__(self, minio_adapter, requests, mlflow_adapter=None, **kwargs):
        super().__init__(**kwargs)
        self.minio_adapter = minio_adapter
        self.mlflow_adapter = mlflow_adapter
        self.requests = requests

    def data_extraction(self, *args, **kwargs):
        raw_pwdb_dataset = self.requests.get(config.PWDB_DATASET_URL, stream=True, timeout=30)
        raw_pwdb_dataset.raise_for_status()
        self.minio_adapter.empty_bucket()
        pwdb_json_dataset = pwdb_transformer.transform_pwdb(json.loads(raw_pwdb_dataset.content))
        self.minio_adapter.put_object(config.SC_PWDB_JSON, json.dumps(pwdb_json_dataset).encode('utf-8'))

    def data_validation(self, *args, **kwargs):
        # TODO: implement me by validating the returned index structure for a start,
        #  and then checking assertions discovered from EDA exercise.
        pass

    def data_preparation(self, *args, **kwargs):
        pwdb_json_dataset = json.loads(self.minio_adapter.get_object(config.SC_PWDB_JSON))
        pwdb_dataframe = pd.DataFrame.from_records(pwdb_json_dataset)
        pwdb_dataframe_columns = self.prepare_pwdb_data(pwdb_dataframe)
        pwdb_target_groups_refactor = self.target_group_refactoring(pwdb_dataframe_columns)
        pwdb_word2vec_model = self.train_pwdb_word2vec_language_model(pwdb_target_groups_refactor)
        pwdb_train_test_data = self.train_pwdb_data(pwdb_target_groups_refactor)
        pwdb_word2vec_pickle = pickle.dumps(pwdb_word2vec_model)
        pwdb_train_test_pickle = pickle.dumps(pwdb_train_test_data)
        self.minio_adapter.put_object("train_test_split.pkl", pwdb_train_test_pickle)


    @staticmethod
    def prepare_pwdb_data(pwdb_dataframe: pd.DataFrame) -> pd.DataFrame:
        """
            Before training the model and applying it to different algorithms, we must prepare the data
            that we extracted. We will work with selected columns which can be viewed down below.
            First of all we must convert the "Target groups" column from a list, into independent strings.
            After that we concatenate "Title, Background information, Content of measure" columns,
            clean them and create separate column named "Descriptive data". As a last step we encode
            "Category, Subcategory, Type of measure" columns to be prepared for classification labels
            for Machine Learning algorithms.

            :return: As a result, we prepared pwdb dataset with common text data prepared classifier
                     labels that will be used into train-test part.
        """
        feature_selector.reduce_array_column(pwdb_dataframe, "Target groups")
        # TODO: train test split with all cols
        # TODO: use of measure, involvement social partener, title
        pwdb_dataframe_columns = pwdb_dataframe[['Title', 'Background information', 'Content of measure',
                                                 'Category', 'Subcategory', 'Type of measure', 'Target groups']]

        pwdb_descriptive_data = pwdb_dataframe_columns['Title'].map(str) + ' ' + \
                                pwdb_dataframe_columns['Background information'].map(str) + ' ' + \
                                pwdb_dataframe_columns['Content of measure'].map(str)
        pwdb_dataframe_columns['Descriptive Data'] = pwdb_descriptive_data \
            .apply(lambda x: data_cleaning.prepare_text_for_cleaning(x))
        pwdb_dataframe_columns = value_replacement.MultiColumnLabelEncoder(
            columns=['Category', 'Subcategory', 'Type of measure']).fit_transform(pwdb_dataframe_columns)

        return pwdb_dataframe_columns

    @staticmethod
    def target_group_refactoring(pwdb_dataframe: pd.DataFrame,
                                 target_group_column_name: str = 'Target groups') -> pd.DataFrame:
        """
            The target group available in the original dataset is very granular. For the purpose of this exercise
            we would benefit from aggregating the target groups into a more generic sets. As a result we will obtain
            target groups on two levels: L1, L2.
            L1: workers, businesses, citizens
            L2: the original set of categories

            :return: the given dataset with an extra column containing the aggregated (L1) values
        """

        refactored_pwdb_df = pwdb_dataframe[target_group_column_name]
        pwdb_dataframe['Businesses'] = refactored_pwdb_df.str.contains('|'.join(BUSINESSES))
        pwdb_dataframe['Citizens'] = refactored_pwdb_df.str.contains('|'.join(CITIZENS))
        pwdb_dataframe['Workers'] = refactored_pwdb_df.str.contains('|'.join(WORKERS))
        refactored_pwdb_df = pd.get_dummies(pwdb_dataframe, columns=[target_group_column_name])
        refactored_pwdb_df.replace({True: 1, False: 0}, inplace=True)

        return refactored_pwdb_df

    @staticmethod
    def train_pwdb_word2vec_language_model(pwdb_dataframe: pd.DataFrame) -> Word2Vec:
        """
            As language model data it will be use "Descriptive Data" column
            and will be transform into word2vec model.
        """
        pwdb_word2vec = Word2Vec(pwdb_dataframe["Descriptive Data"])

        return pwdb_word2vec

    @staticmethod
    def train_pwdb_data(pwdb_dataframe: pd.DataFrame) -> dict:
        """
            After data preparation step, we have to split existent data into training and testing size.
            The inputs will be "Descriptive data" and "Category, Subcategory, Type of measure,
            Target groups L1 and Target groups L2" columns.

            :return: As a result, we will have a dictionary with split data.
        """
        pwdb_common_text = pwdb_dataframe['Descriptive Data']
        pwdb_classifiers = pwdb_dataframe.drop(['Descriptive Data', 'Title',
                                                'Background information', 'Content of measure'], axis=1)
        # pwdb_word2vec = Word2Vec(pwdb_common_text, window=5, min_count=10, size=300)
        x_train, x_test, y_train, y_test = model_selection.train_test_split(pwdb_common_text, pwdb_classifiers,
                                                                            random_state=42, test_size=0.3,
                                                                            shuffle=True)
        train_test_dict = {"X_train": x_train, "X_test": x_test, "y_train": y_train, "y_test": y_test}

        return train_test_dict

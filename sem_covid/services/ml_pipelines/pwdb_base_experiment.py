#!/usr/bin/python3

# pwdb_base_experiment.py
# Date:  22/03/2021
# Author: Chiriac Dan
# Email: dan.chiriac1453@gmail.com

"""
    This module deals with the PWDB ML experiment specificities.
"""

import logging
import pickle
from abc import ABC

import pandas as pd
from sklearn import model_selection

from sem_covid.services.base_pipeline import BaseExperiment
from sem_covid.services.data_registry import Dataset
from sem_covid.services.sc_wrangling import data_cleaning
from sem_covid.services.sc_wrangling import feature_selector
from sem_covid.services.sc_wrangling import value_replacement

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
        pass

    def data_validation(self, *args, **kwargs):
        # TODO: implement me by validating the returned index structure for a start,
        #  and then checking assertions discovered from EDA exercise.
        pass

    def data_preparation(self, *args, **kwargs):
        pwdb_dataset = Dataset.PWDB.fetch()
        pwdb_dataframe_columns = self.prepare_pwdb_data(pwdb_dataset)
        pwdb_target_groups_refactor = self.target_group_refactoring(pwdb_dataframe_columns)
        pwdb_train_test_data = self.train_pwdb_data(pwdb_target_groups_refactor)
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
        target_featuring = feature_selector.reduce_array_column(pwdb_dataframe, "target_groups")
        pwdb_descriptive_data = target_featuring['title'].map(str) + ' ' + \
            target_featuring['background_info_description'].map(str) + ' ' + \
            target_featuring['content_of_measure_description'].map(str) + ' ' + \
            target_featuring['use_of_measure_description'] + ' ' + \
            target_featuring['involvement_of_social_partners_description']

        # TODO: see that the text cleaning is considered (stop words removed for now)
        target_featuring['descriptive_data'] = pwdb_descriptive_data \
            .apply(lambda x: data_cleaning.clean_remove_stopwords(x))
        pwdb_dataframe_columns = value_replacement.MultiColumnLabelEncoder(
            columns=['category', 'subcategory', 'type_of_measure']).fit_transform(target_featuring)

        return pwdb_dataframe_columns

    @staticmethod
    def target_group_refactoring(pwdb_dataframe: pd.DataFrame,
                                 target_group_column_name: str = 'target_groups') -> pd.DataFrame:
        """
            The target group available in the original dataset is very granular. For the purpose of this exercise
            we would benefit from aggregating the target groups into a more generic sets. As a result we will obtain
            target groups on two levels: L1, L2.
            L1: workers, businesses, citizens
            L2: the original set of categories

            :return: the given dataset with an extra column containing the aggregated (L1) values
        """

        refactored_pwdb_df = pwdb_dataframe[target_group_column_name]
        pwdb_dataframe['businesses'] = refactored_pwdb_df.str.contains('|'.join(BUSINESSES))
        pwdb_dataframe['citizens'] = refactored_pwdb_df.str.contains('|'.join(CITIZENS))
        pwdb_dataframe['workers'] = refactored_pwdb_df.str.contains('|'.join(WORKERS))
        # refactored_pwdb_df = pd.get_dummies(pwdb_dataframe, columns=[target_group_column_name])
        pwdb_dataframe.replace({True: 1, False: 0}, inplace=True)

        return pwdb_dataframe

    @staticmethod
    def train_pwdb_data(pwdb_dataframe: pd.DataFrame) -> dict:
        """
            After data preparation step, we have to split existent data into training and testing size.
            The inputs will be "Descriptive data" and "Category, Subcategory, Type of measure,
            Target groups L1 and Target groups L2" columns.

            :return: As a result, we will have a dictionary with split data.
        """
        pwdb_common_text = pwdb_dataframe.drop(['category', 'subcategory', 'type_of_measure',
                                                'businesses', 'citizens', 'workers'], axis=1)
        pwdb_classifiers = pwdb_dataframe[['category', 'subcategory', 'type_of_measure',
                                           'businesses', 'citizens', 'workers']]
        x_train, x_test, y_train, y_test = model_selection.train_test_split(pwdb_common_text, pwdb_classifiers,
                                                                            random_state=42, test_size=0.3,
                                                                            shuffle=True)
        train_test_dict = {"X_train": x_train, "X_test": x_test, "y_train": y_train, "y_test": y_test}

        return train_test_dict

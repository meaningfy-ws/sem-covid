#!/usr/bin/python3

# pwdb_base_experiment.py
# Date:  22/03/2021
# Author: Chiriac Dan
# Email: dan.chiriac1453@gmail.com

"""
    Base class for all experiments performed on PDWB dataset.
    The common part to all ML experiments is tha data loading, extraction and preparation.
"""

import logging
import requests
import pickle
from abc import ABC
from json import loads, dumps

from jq import compile
import pandas as pd
from gensim.models import Word2Vec
from sklearn.model_selection import train_test_split

from ml_experiments.services.sc_wrangling.pwdb_transformer import get_transformation_rules
from ml_experiments.services.sc_wrangling.feature_selector import (reduce_array_column,
                                                                   multi_label_column_to_binary_columns)
from ml_experiments.services.sc_wrangling.data_cleaning import prepare_text_for_cleaning
from ml_experiments.services.sc_wrangling.value_replacement import MultiColumnLabelEncoder
from ml_experiments.adapters.minio_adapter import MinioAdapter
from ml_experiments.services.base_experiment import BaseExperiment

logger = logging.getLogger(__name__)

ML_EXPERIMENTS_BUCKET_NAME = "ml-experiments"
SC_COVID_JSON = "covid19.json"
SC_COVID_DATASET = "pwdb_dataset.pkl"

PWDB_DATASET_URL = 'http://static.eurofound.europa.eu/covid19db/data/covid19db.json'
MINIO_ACCESS_KEY = '2zVld17bTfKk8iu0Eh9H74MywAeDV3WQ'
MINIO_SECRET_KEY = 'ddk9fixfI9qXiMaZu1p2a7BsgY2yDopm'
MINIO_URL = 'srv.meaningfy.ws:9000'

transformation = '''{
"Identifier": .recordId,
"Title": .fieldData.title,
"Title (national language)": .fieldData.title_nationalLanguage,
"Country": .fieldData.calc_country,
"Start date": .fieldData.d_startDate,
"End date": .fieldData.d_endDate,
"Date type": .fieldData.dateType,
"Type of measure": .fieldData.calc_type,
"Status of regulation": .fieldData.statusOfRegulation,
"Category": .fieldData.calc_minorCategory,
"Subcategory": .fieldData.calc_subMinorCategory,
"Case added": .fieldData.calc_creationDay,
"Background information": .fieldData.descriptionBackgroundInfo,
"Content of measure": .fieldData.descriptionContentOfMeasure,
"Use of measure": .fieldData.descriptionUseOfMeasure,
"Actors": [.portalData.actors[] |  ."actors::name" ],
"Target groups": [.portalData.targetGroups[] | ."targetGroups::name"],
"Funding": [.portalData.funding[] | ."funding::name" ],
"Views of social partners": .fieldData.descriptionInvolvementOfSocialPartners,
"Form of social partner involvement": .fieldData.socialPartnerform,
"Role of social partners": .fieldData.socialPartnerrole,
"Is sector specific": .fieldData.isSector,
"Private or public sector": .fieldData.sector_privateOrPublic,
"Is occupation specific": .fieldData.isOccupation,
"Sectors": [.portalData.sectors[] | ."sectors::name" ],
"Occupations": [.portalData.occupations[] | .],
"Sources": [.portalData.sources[] | ."sources::url" ],
}'''


class PWDBBaseExperiment(BaseExperiment):

    def data_extraction(self, *args, **kwargs):
        response = requests.get(PWDB_DATASET_URL, stream=True, timeout=30)
        response.raise_for_status()
        minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, ML_EXPERIMENTS_BUCKET_NAME)
        minio.empty_bucket()
        transformed_json = compile(get_transformation_rules(transformation)).input(loads(response.content)).all()
        minio.put_object(SC_COVID_JSON, dumps(transformed_json).encode('utf-8'))
        dataframe_from_json = pd.DataFrame.from_records(transformed_json)
        convert_to_pickle = pickle.dumps(dataframe_from_json)
        minio.put_object("pwdb_dataset.pkl", convert_to_pickle)

    def data_validation(self, *args, **kwargs):
        # TODO: implement me by validating the returned index structure for a start,
        #  and then checking assertions discovered from EDA exercise.
        raise NotImplementedError

    def data_preparation(self, *args, **kwargs):
        # Connect to MinIO server
        minio = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, ML_EXPERIMENTS_BUCKET_NAME)
        dataframe = pickle.loads(minio.get_object(SC_COVID_DATASET))
        # Begin preparation
        reducer = reduce_array_column(dataframe, "Target groups")
        df = reducer[['Title', 'Background information', 'Content of measure',
                      'Category', 'Subcategory', 'Type of measure', 'Target groups']]
        # Prepare independent data
        df_description_data = df['Title'].map(str) + df['Background information'].map(str) + \
                              df['Content of measure'].map(str)
        concatenate_df = pd.DataFrame(df_description_data, columns=['Concatenated Data'])
        df['Concatenated Data'] = concatenate_df
        df['Concatenated Data (clean)'] = df['Concatenated Data'].apply(lambda x: prepare_text_for_cleaning(x))
        # Prepare label data
        selected_data = df[['Concatenated Data (clean)', 'Category', 'Subcategory', 'Type of measure', 'Target groups']]
        label_encoding = MultiColumnLabelEncoder(
            columns=['Category', 'Subcategory', 'Type of measure']).fit_transform(selected_data)
        multi_label_target_groups = multi_label_column_to_binary_columns(label_encoding, "Target groups")
        target_groups_values = multi_label_target_groups['Target groups']
        businesses = ['Companies providing essential services', 'Contractors of a company',
                      'Larger corporations', 'One person or microenterprises', 'Other businesses',
                      'SMEs', 'Sector specific set of companies', 'Solo-self-employed', 'Start-ups']

        citizens = ['Children (minors)', 'Disabled', 'Migrants', 'Older citizens',
                    'Other groups of citizens', 'Parents', 'People in care facilities', 'Refugees',
                    'Single parents', 'The COVID-19 risk group', 'Women', 'Youth (18-25)']

        workers = ['Cross-border commuters', 'Disabled workers', 'Employees in standard employment',
                   'Female workers', 'Migrants in employment', 'Older people in employment (aged 55+)',
                   'Other groups of workers', 'Parents in employment', 'Particular professions',
                   'Platform workers', 'Posted workers', 'Refugees in employment', 'Seasonal workers',
                   'Self-employed', 'Single parents in employment', 'The COVID-19 risk group at the workplace',
                   'Undeclared workers', 'Unemployed', 'Workers in care facilities',
                   'Workers in essential services', 'Workers in non-standard forms of employment',
                   'Youth (18-25) in employment']

        multi_label_target_groups['Businesses'] = target_groups_values.str.contains('|'.join(businesses))
        multi_label_target_groups['Citizens'] = target_groups_values.str.contains('|'.join(citizens))
        multi_label_target_groups['Workers'] = target_groups_values.str.contains('|'.join(workers))
        multi_label_target_groups.replace({True: 1, False: 0}, inplace=True)
        convert_to_pickle = pickle.dumps(multi_label_target_groups)
        minio.put_object("pwdb_prepared.pkl", convert_to_pickle)
        # Split data for train, test and word model training
        independent_data = multi_label_target_groups['Concatenated Data (clean)']
        label_data = multi_label_target_groups.drop(['Concatenated Data (clean)', 'Target groups'], axis=1)
        pwdb_word2vec = Word2Vec(independent_data, window=5, min_count=10, size=300)
        w2v_saving = pickle.dumps(pwdb_word2vec)
        minio.put_object("word2vec.gensim.model", w2v_saving)
        x_train, x_test, y_train, y_test = train_test_split(independent_data, label_data,
                                                            random_state=42, test_size=0.3, shuffle=True)
        train_test_dict = {"X_train": x_train, "X_test": x_test, "y_train": y_train, "y_test": y_test}
        convert_to_pickle = pickle.dumps(train_test_dict)
        minio.put_object("train_test_split.pkl", convert_to_pickle)

    def model_training(self, *args, **kwargs):
        pass

    def model_evaluation(self, *args, **kwargs):
        pass

    def model_validation(self, *args, **kwargs):
        pass


pwdb_caller = PWDBBaseExperiment()
pwdb_caller.data_preparation()


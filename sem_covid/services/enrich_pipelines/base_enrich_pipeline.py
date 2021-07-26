#!/usr/bin/python3

# base_enrich_pipeline.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to define a basic pipeline for enriching a dataset
     based on drive classification models and stored in MlFlow.
"""
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
# from pycaret.classification import predict_model
from sklearn import preprocessing

from sem_covid.services.data_registry import LanguageModel
from sem_covid.services.model_registry import ClassificationModel
from sem_covid.services.sc_wrangling.mean_vectorizer import text_to_vector
from sem_covid.services.store_registry import store_registry

EMBEDDING_COLUMN = "embeddings"

CLASS_NAMES = ['businesses', 'citizens', 'workers', 'category', 'subcategory', 'type_of_measure', 'funding']

CLASS_NAMES_WITH_LABEL = ['category', 'subcategory', 'type_of_measure', 'funding']

PWDB_FEATURES_Y = 'fs_pwdb_y'


class BasePrepareDatasetPipeline:
    """
        This class aims to define a pipeline for the preparation part of the dataset before enrichment.
        The preparation steps are:
        - loading the dataset from ElasticSearch
        - loading the language model from MinIO
        - preparing the text fields in the dataset
        - creating embeddings vectors for the text fields
        - storing features in FeatureStore
    """

    def __init__(self, textual_columns: list, ds_es_index: str, features_store_name: str):
        """
            Initialization of parameters for the basic prepare pipeline
        :param ds_es_index: the index of a dataset in ElasticSearch
        :param features_store_name: the name of a features store

        """
        self.ds_es_index = ds_es_index
        self.features_store_name = features_store_name
        self.dataset = pd.DataFrame()
        self.l2v_dict = {}
        self.textual_columns = textual_columns

    def load_dataset(self):
        """
            At this stage, the dataset is loaded from Elastic Store
        """
        es_store = store_registry.es_index_store()
        self.dataset = es_store.get_dataframe(self.ds_es_index)
        assert self.dataset is not None
        assert len(self.dataset) > 0

    def load_language_models(self):
        """
           At this stage, the language model is loaded, which is used to calculate word embeddings
        """
        law2vec = LanguageModel.LAW2VEC.fetch()
        law2vec_path = LanguageModel.LAW2VEC.path_to_local_cache()
        self.l2v_dict = KeyedVectors.load_word2vec_format(law2vec_path, encoding="utf-8")

    def prepare_textual_columns(self):
        """
            This step is dedicated to preparing textual data from the dataset
        """
        text_df = pd.DataFrame(self.dataset[self.textual_columns])
        text_df.replace(np.nan, '', regex=True, inplace=True)
        text_df[EMBEDDING_COLUMN] = text_df.agg(' '.join, axis=1)
        text_df.reset_index(drop=True, inplace=True)
        self.dataset = text_df

    def create_embeddings(self):
        """
            This step is dedicated to calculating word embeddings
        """
        self.dataset[EMBEDDING_COLUMN] = self.dataset[EMBEDDING_COLUMN].apply(
            lambda x: text_to_vector(x, self.l2v_dict))

    def store_features(self):
        """
            This step is used to store calculated features in the Feature Store
        """
        assert EMBEDDING_COLUMN in self.dataset
        feature_store = store_registry.es_feature_store()
        input_features_name = self.features_store_name + '_x'
        matrix_df = pd.DataFrame(list(self.dataset[EMBEDDING_COLUMN].values))
        feature_store.put_features(features_name=input_features_name, content=matrix_df)

    def execute(self):
        """
            This method is used to perform the steps in the defined order
        """
        self.load_dataset()
        self.load_language_models()
        self.prepare_textual_columns()
        self.create_embeddings()
        self.store_features()


class BaseEnrichPipeline:
    """
        This class aims to define a basic pipeline for the enrichment part of the dataset with new fields.

        The enrichment steps are:
       - loading the dataset
       - loading the features
       - loading the trained classification mode
       - enriching the dataset with the help of the trained model
       - storing the enriched dataset in the ElasticStore

    """

    def __init__(self, feature_store_name: str, ds_es_index: str, class_names: list = None,
                 class_names_with_label: list = None):
        """
            Initialization of parameters for enrichment pipelines.
        :param feature_store_name: the name for the feature store
        :param ds_es_index: the name of the index for the dataset
        :param class_names: the name of the classes that will be added to the dataset
        :param class_names_with_label: the name of the classes that will be added to the dataset,
                                        which have a textual notation
        """
        self.feature_store_name = feature_store_name
        self.ds_es_index = ds_es_index
        self.class_names = class_names if class_names else CLASS_NAMES
        self.class_names_with_label = class_names_with_label if class_names_with_label else CLASS_NAMES_WITH_LABEL
        self.models = {}
        self.features = pd.DataFrame()
        self.dataset = pd.DataFrame()
        self.label_features = pd.DataFrame()

    def load_dataset(self):
        """
            This step loads the desired dataset.
        """
        es_store = store_registry.es_index_store()
        dataset = es_store.get_dataframe(index_name=self.ds_es_index)
        assert dataset is not None
        assert len(dataset) > 0
        self.dataset = dataset

    def load_features(self):
        """
            This step loads features that will be used for classification.
        """
        input_features_name = self.feature_store_name + '_x'
        output_features_name = PWDB_FEATURES_Y
        feature_store = store_registry.es_feature_store()
        input_features = feature_store.get_features(features_name=input_features_name)
        output_features = feature_store.get_features(features_name=output_features_name)
        assert input_features is not None
        assert len(input_features) > 0
        assert output_features is not None
        assert len(output_features) > 0
        self.features = input_features
        self.label_features = output_features

    def load_ml_flow_models(self):
        """
            This step loads the classification template from MlFlow.
        """
        self.models = {}
        for class_name in self.class_names:
            self.models[class_name] = ClassificationModel.pwdb_by_class_name(class_name=class_name)

    def enrich_dataset(self):
        """
            This step enriches the dataset based on the classification model.
        """
        for class_name in self.class_names:
            model = self.models[class_name]
            dataset = self.features
            dataset[class_name] = 0
            enriched_df = predict_model(model, data=dataset)
            self.dataset[class_name] = enriched_df['Label'].values
        for class_name in self.class_names_with_label:
            le = preprocessing.LabelEncoder()
            le.fit(self.label_features[class_name + '_label'])
            self.dataset[class_name] = le.inverse_transform(self.dataset[class_name])

    def store_dataset_in_es(self):
        """
            This step writes the enriched dataset in ElasticStore.
        """
        for class_name in self.class_names:
            assert class_name in self.dataset.columns
        es_client = store_registry.es_index_store()
        new_index_name = self.ds_es_index + '_enriched'
        self.dataset.reset_index(drop=True, inplace=True)
        es_client.put_dataframe(index_name=new_index_name, content=self.dataset)

    def execute(self):
        """
            This method aims to perform the steps in the defined order.
        """
        self.load_dataset()
        self.load_features()
        self.load_ml_flow_models()
        self.enrich_dataset()
        self.store_dataset_in_es()

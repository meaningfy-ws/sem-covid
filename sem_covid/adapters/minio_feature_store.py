#!/usr/bin/python3

# minio_feature_store.py
# Date:  21.07.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import pandas as pd

from sem_covid.adapters.abstract_store import FeatureStoreABC, ObjectStoreABC
import pickle


class MinioFeatureStore(FeatureStoreABC):

    def __init__(self, object_store: ObjectStoreABC):
        self._object_store = object_store

    def get_features(self, features_name: str) -> pd.DataFrame:
        return pickle.loads(self._object_store.get_object(object_name=features_name))

    def put_features(self, features_name: str, content: pd.DataFrame):
        self._object_store.put_object(object_name=features_name, content=pickle.dumps(content))

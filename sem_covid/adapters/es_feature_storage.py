from sem_covid.adapters.abstract_storage import FeatureStorageABC, IndexStorageABC
import pandas as pd


class ESFeatureStorage(FeatureStorageABC):

    def __init__(self, index_storage: IndexStorageABC):
        self._index_storage = index_storage

    def get_features(self, features_name: str) -> pd.DataFrame:
        return self._index_storage.get_dataframe(index_name=features_name)

    def put_features(self, features_name: str, content: pd.DataFrame):
        return self._index_storage.put_dataframe(index_name=features_name, content=content)

from sem_covid.adapters.abstract_store import FeatureStoreABC, IndexStoreABC
import pandas as pd


class ESFeatureStore(FeatureStoreABC):

    def __init__(self, index_store: IndexStoreABC):
        self._index_store = index_store

    def get_features(self, features_name: str) -> pd.DataFrame:
        return self._index_store.get_dataframe(index_name=features_name)

    def put_features(self, features_name: str, content: pd.DataFrame):
        return self._index_store.put_dataframe(index_name=features_name, content=content)

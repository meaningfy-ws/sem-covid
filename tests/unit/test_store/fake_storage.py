import copy

from sem_covid.adapters.abstract_store import *


class FakeObjectStore(ObjectStoreABC):

    def __init__(self):
        self._objects = dict()

    def clear_storage(self, object_name_prefix=None):
        tmp_dict = dict.fromkeys(self._objects.keys(), [])
        for key in tmp_dict.keys():
            str_key = str(key)
            if str_key.startswith(object_name_prefix):
                del self._objects[key]

    def put_object(self, object_name: str, content) -> int:
        self._objects[object_name] = content

    def get_object(self, object_name: str):
        if object_name in self._objects.keys():
            return self._objects[object_name]
        else:
            return None

    def list_objects(self, object_name_prefix: str):
        list_result = []
        for key in self._objects.keys():
            str_key = str(key)
            if str_key.startswith(object_name_prefix):
                list_result.append(self._objects[key])
        return list_result


class FakeSecretsStore(SecretsStoreABC):
    def get_secrets(self, path: str) -> dict:
        secrets = {
            "secret_path1":
                {
                    "secret1": "white",
                    "secret2": "black"
                },
            "secret_path2":
                {
                    "secret3": "orange",
                    "secret4": "green"
                }

        }
        return secrets[path]


class FakeIndexStore(IndexStoreABC):

    def __init__(self):
        self._store = dict()

    def index(self, index_name, document_id, document_body):
        pass

    def get_document(self, index_name: str, document_id: str):
        pass

    def search(self, index_name: str, query: str, exclude_binary_source: bool = True):
        pass

    def get_dataframe(self, index_name: str) -> pd.DataFrame:
        if index_name in self._store:
            return self._store[index_name]
        else:
            return None

    def put_dataframe(self, index_name: str, content: pd.DataFrame):
        self._store[index_name] = content

    def dump(self, index_name: str, file_name: str, local_path: pathlib.Path = None,
             remote_store: ObjectStoreABC = None):
        pass


class FakeFeatureStore(FeatureStoreABC):

    def __init__(self):
        self._store = dict()

    def get_features(self, features_name: str) -> pd.DataFrame:
        if features_name in self._store:
            return self._store[features_name]
        else:
            return None

    def put_features(self, features_name: str, content: pd.DataFrame):
        self._store[features_name] = content


class FakeTripleStore(TripleStoreABC):
    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> 'TripleStoreABC':
        return self

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'TripleStoreABC':
        return self

    def get_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([{"col1": "A", "col2": "B"}])

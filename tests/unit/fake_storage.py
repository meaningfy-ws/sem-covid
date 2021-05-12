from sem_covid.adapters.abstract_storage import *


class FakeObjectStorage(ObjectStorageABC):

    def clear_storage(self, object_name_prefix=None):
        pass

    def put_object(self, object_name: str, content) -> int:
        pass

    def get_object(self, object_name: str):
        pass

    def list_objects(self, object_prefix: str):
        pass


class FakeSecretsStorage(SecretsStorageABC):
    def get_secrets(self, path: str) -> dict:
        pass


class FakeIndexStorage(IndexStorageABC):
    def index(self, index_name, document_id, document_body):
        pass

    def get_document(self, index_name: str, document_id: str):
        pass

    def search(self, index_name: str, query: str, exclude_binary_source: bool = True):
        pass

    def get_dataframe(self, index_name: str) -> pd.DataFrame:
        pass

    def put_dataframe(self, index_name: str, content: pd.DataFrame):
        pass

    def dump(self, index_name: str, file_name: str, local_path: pathlib.Path = None,
             remote_storage: ObjectStorageABC = None):
        pass


class FakeFeatureStorage(FeatureStorageABC):
    def get_features(self, features_name: str) -> pd.DataFrame:
        pass

    def put_features(self, features_name: str, content: pd.DataFrame):
        pass


class FakeTripleStorage(TripleStorageABC):
    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> 'TripleStorageABC':
        pass

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'TripleStorageABC':
        pass

    def get_dataframe(self) -> pd.DataFrame:
        pass

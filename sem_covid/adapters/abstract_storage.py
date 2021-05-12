from abc import ABC, abstractmethod
import pandas as pd
import pathlib


class ObjectStorageABC(ABC):

    @abstractmethod
    def clear_storage(self, object_name_prefix=None):
        raise NotImplementedError

    @abstractmethod
    def put_object(self, object_name: str, content) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_object(self, object_name: str):
        raise NotImplementedError

    @abstractmethod
    def list_objects(self, object_prefix: str):
        raise NotImplementedError


class SecretsStorageABC(ABC):

    @abstractmethod
    def get_secrets(self, path: str) -> dict:
        raise NotImplementedError


class IndexStorageABC(ABC):

    @abstractmethod
    def index(self, index_name, document_id, document_body):
        raise NotImplementedError

    @abstractmethod
    def get_document(self, index_name: str, document_id: str):
        raise NotImplementedError

    @abstractmethod
    def search(self, index_name: str, query: str, exclude_binary_source: bool = True):
        raise NotImplementedError

    @abstractmethod
    def get_dataframe(self, index_name: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def put_dataframe(self, index_name: str, content: pd.DataFrame):
        raise NotImplementedError

    @abstractmethod
    def dump(self, index_name: str, file_name: str, local_path: pathlib.Path = None,
             remote_storage: ObjectStorageABC = None):
        raise NotImplementedError


class FeatureStorageABC(ABC):

    @abstractmethod
    def get_features(self, features_name: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def put_features(self, features_name: str, content: pd.DataFrame):
        raise NotImplementedError


class TripleStorageABC(ABC):

    @abstractmethod
    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> 'TripleStorageABC':
        raise NotImplementedError

    @abstractmethod
    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'TripleStorageABC':
        raise NotImplementedError

    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        raise NotImplementedError

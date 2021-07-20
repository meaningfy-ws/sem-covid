#!/usr/bin/python3

# abstract_store.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to define interfaces for different types of stores that are used in the project.
"""

from abc import ABC, abstractmethod
import pandas as pd
import pathlib


class ObjectStoreABC(ABC):
    """
        This class defines the abstraction for an object store, based on S3 technology.
    """

    @abstractmethod
    def empty_bucket(self, object_name_prefix: str = None):
        """
            This method deletes all stored objects that begin with a specific prefix.
        :param object_name_prefix: the prefix that will be searched in the name of the stored objects.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def put_object(self, object_name: str, content) -> int:
        """
            This method allows you to store an object with a name so that it can be found later.
        :param object_name: the name of the object to be stored
        :param content: the content of the object to be stored
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_object(self, object_name: str):
        """
            This method allows you to extract an object based on its name.
        :param object_name: the name of the desired object to be extracted
        :return: returns the requested object based on the transmitted object_name
        """
        raise NotImplementedError

    @abstractmethod
    def list_objects(self, object_name_prefix: str):
        """
            This method returns a list of objects that have been stored
             and whose names begin with the prefix transmitted.
        :param object_name_prefix: the prefix of the name based on which the objects will be searched
        :return: returns a list of objects beginning with the prefix transmitted by object_name_prefix
        """
        raise NotImplementedError


class SecretsStoreABC(ABC):
    """
        This class aims to define an interface for obtaining secrets from similar resources as Vault.
    """

    @abstractmethod
    def get_secrets(self, path: str) -> dict:
        """
            This method defines abstraction to obtain a dictionary of secrets based on a direction to them.
        :param path: the direction of secrets
        :return: returns a dictionary of secrets
        """
        raise NotImplementedError


class IndexStoreABC(ABC):
    """
        This class defines an abstraction for Elastic Store.
    """

    @abstractmethod
    def index(self, index_name: str, document_id, document_body):
        """
            TODO: to document this method
        :param index_name:
        :param document_id:
        :param document_body:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_document(self, index_name: str, document_id: str):
        """
            This method returns a document based on document_id and index_name.
        :param index_name: the name of the index in the storage
        :param document_id: the id of the searched document
        :return: returns a document from IndexStore
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, index_name: str, query: str, exclude_binary_source: bool = True):
        """
            This method provides in-store query functionality.
        :param index_name: the name of the index in the store
        :param query: the body of the desired query
        :param exclude_binary_source: flag to exclude binary sources
        :return: returns a list of documents based on the suggested query
        """
        raise NotImplementedError

    @abstractmethod
    def get_dataframe(self, index_name: str) -> pd.DataFrame:
        """
            This method returns a complete index from the store as a DataFrame.
        :param index_name: the name of the desired index
        :return: returns a DataFrame generated from the store index
        """
        raise NotImplementedError

    @abstractmethod
    def put_dataframe(self, index_name: str, content: pd.DataFrame):
        """
            This method transforms the received DataFrame and loads it as an index in the store.
        :param index_name: the name of the new index that will be created based on the received DataFrame
        :param content: the DataFrame content to be stored in the index
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def dump(self, index_name: str, file_name: str, local_path: pathlib.Path = None,
             remote_store: ObjectStoreABC = None):
        """
            This method allows you to dump an index on a local file or a remote object store.
        :param index_name: the name of the index to be dumped
        :param file_name: the name of the file where the dump will be made
        :param local_path: the path to the file system when performing the local dump
        :param remote_store: a remote object store, where the index will be stored as file_name
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def create_index(self, index_name: str, index_mappings: dict, exist_ok=True):
        """
        Create an index if it doesn't exist already-
        """

        raise NotImplementedError


class FeatureStoreABC(ABC):
    """
       This class is an abstraction for a feature store.
       The purpose of the feature store is to provide a simple method of management
       of the features identified in a machine learning experiment.
    """

    @abstractmethod
    def get_features(self, features_name: str) -> pd.DataFrame:
        """
            This method provides extraction features in the form of a DataFrame.
        :param features_name: the name of the features to be extracted
        :return: returns a DataFrame with features
        """
        raise NotImplementedError

    @abstractmethod
    def put_features(self, features_name: str, content: pd.DataFrame):
        """
            This method allows to store a DataFrame with features based on the name in features_name.
        :param features_name: the name of the features to be stored
        :param content: the DataFrame content in which features are stored
        :return:
        """
        raise NotImplementedError


class TripleStoreABC(ABC):
    """
        This class provides an abstraction for a TripleStore.
    """

    @abstractmethod
    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> 'TripleStoreABC':
        """
            TODO: to document this method.
        :param sparql_query:
        :param substitution_variables:
        :param sparql_prefixes:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> 'TripleStoreABC':
        """
            TODO: to document this method.
        :param sparql_query_file_path:
        :param substitution_variables:
        :param prefixes:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        """
            TODO: to document this method.
        :return:
        """
        raise NotImplementedError

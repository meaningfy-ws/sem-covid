#!/usr/bin/python3

# artifacts.py
# Date:  12/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This module provides base datasource proxies. An unified layer to access the data.
    The proxies act as gateways to the actual dataset objects encapsulating the access configurations.
"""
import logging
import pathlib
import pickle
import tempfile
from abc import ABC, abstractmethod
from builtins import NotImplementedError
from typing import Any, Union

import pandas as pd

from sem_covid.adapters.abstract_store import IndexStoreABC, ObjectStoreABC

logger = logging.getLogger(__name__)


class BaseDataSource(ABC):
    _temporary_file: tempfile.NamedTemporaryFile
    _object_name: str

    def __init__(self, enable_caching: bool = True):
        self._temporary_file = None
        self._enable_caching = enable_caching
        self._object_name = None

    def fetch(self) -> Any:
        """
            Fetch the content from the remote source or the local cache if available.
        :return:
        """
        if self._enable_caching:
            if not self._temporary_file:
                self._temporary_file = tempfile.NamedTemporaryFile()
                logger.info(f'Fetching {self._object_name} from the remote source')
                content = self._fetch()
                self._to_local_cache(content)
                return content
            else:
                logger.info(f'Fetching {self._object_name} from the local cache')
                return self._from_local_cache()
        else:
            logger.info(f'Fetching {self._object_name} from the remote source')
            return self._fetch()

    @abstractmethod
    def _fetch(self) -> Any:
        """
            Establish the connection and fetch the content from the remote source
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def _to_local_cache(self, content):
        """
            Save the content temporarily on the local system
        :param content:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def _from_local_cache(self):
        """
            Return the temporary content from the local system
        :return:
        """
        raise NotImplementedError

    def __del__(self):
        """
            Clean up when done
        :return:
        """
        if self._temporary_file:
            self._temporary_file.close()

    def path_to_local_cache(self) -> Union[pathlib.Path, None]:
        if not self._enable_caching:
            return None

        if not self._temporary_file:
            self.fetch()
        return pathlib.Path(self._temporary_file.name)


class BinaryDataSource(BaseDataSource):
    """
        A binary Minio/S3 datasource proxy with local caching
    """
    _object_storage: ObjectStoreABC
    _object_path: str

    def __init__(self, object_path: str, object_storage: ObjectStoreABC, enable_caching: bool = True):
        super().__init__(enable_caching)
        self._object_path = object_path
        self._object_storage = object_storage

    def _fetch(self) -> bytes:
        return self._object_storage.get_object(self._object_path)

    def _to_local_cache(self, content: bytes):
        logger.info('Caching the content locally at ' + self._temporary_file.name)
        self.path_to_local_cache().write_bytes(content)

    def _from_local_cache(self) -> bytes:
        self.path_to_local_cache().read_bytes()


class TabularDataSource(BaseDataSource):

    def _fetch(self) -> Any:
        raise NotImplementedError

    def _to_local_cache(self, content: pd.DataFrame):
        pkl_bytes = pickle.dumps(content)
        return self.path_to_local_cache().write_bytes(pkl_bytes)

    def _from_local_cache(self) -> pd.DataFrame:
        pkl_bytes = self.path_to_local_cache().read_bytes()
        return pickle.loads(pkl_bytes)


class IndexTabularDataSource(TabularDataSource):
    """
        A datasource proxy returning Pandas Dataframe from elasticsearch indexes with local caching
    """
    _index_store: IndexStoreABC

    def __init__(self, index_name: str, index_store: IndexStoreABC, enable_caching: bool = True):
        super().__init__(enable_caching)
        self._object_name = index_name
        self._index_store = index_store

    def _fetch(self) -> pd.DataFrame:
        return self._index_store.get_dataframe(index_name=self._object_name)

    def dump_local(self, local_path: pathlib.Path):
        file_name = self._object_name + ".json"
        self._index_store.dump(self._object_name, file_name, local_path=local_path)

    def dump_remote(self, remote_store: ObjectStoreABC):
        file_name = self._object_name + ".json"
        self._index_store.dump(self._object_name, file_name, remote_store=remote_store)

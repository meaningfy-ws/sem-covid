#!/usr/bin/python3

# artifacts.py
# Date:  12/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This module provides base datasource proxies.
    The proxies act as gateways to the actual dataset objects encapsulating teh access configurations.
"""
import pathlib
import tempfile
from abc import ABC
from builtins import NotImplementedError

import pandas as pd


class BinaryCachedDataSource(ABC):
    """
        Base binary datasource proxy with local caching feature
    """

    _temporary_file: tempfile.NamedTemporaryFile

    def __init__(self):
        self._temporary_file = None

    def fetch(self) -> bytes:
        """
            Fetch the bytes from the remote source or the local cache if available.
        :return:
        """
        if not self._temporary_file:
            content = self._fetch()
            self._to_local_cache(content)
            return content
        else:
            return self._from_local_cache()

    def _fetch(self) -> bytes:
        raise NotImplementedError

    def path_to_local_cache(self) -> pathlib.Path:
        if not self._temporary_file:
            self.fetch()
        return pathlib.Path(self._temporary_file.name)

    def _to_local_cache(self, content: bytes):
        if not self._temporary_file:
            self._temporary_file = tempfile.NamedTemporaryFile()
        self.path_to_local_cache().write_bytes(content)

    def _from_local_cache(self) -> bytes:
        self.path_to_local_cache().read_bytes()

    def __del__(self):
        if self._temporary_file:
            self._temporary_file.close()


class TabularDatasource(ABC):
    """
        Base tabular datasource proxy
    """

    def __init__(self):
        self.temporary_file = None

    def fetch_dataframe(self) -> pd.DataFrame:
        raise NotImplementedError

    def path_to_local_cache(self) -> pathlib.Path:
        return pathlib.Path(self.temporary_file.name)

    def _fetch_json(self):
        raise NotImplementedError

    def clear_cache(self):
        """

        :return:
        """
        if self.temporary_file:
            self.temporary_file.close()

    def __del__(self):
        self.clear_cache()

#!/usr/bin/python3

# data.py
# Date:  19/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    A registry of the frequently used datasets and language models
"""
from ml_experiments.services.base_data_source import BinaryDatasource


class Dataset(object):
    # PWDB = FakeTabularDatasource()
    # EU_CELLAR = FakeTabularDatasource()
    # EU_ACTION_TIMELINE = FakeTabularDatasource()
    # IRELAND_ACTION_TIMELINE = FakeTabularDatasource()
    ...


class LanguageModel(object):
    # LAW2VEC = FakeTabularDatasource()
    # JRC2VEC = FakeTabularDatasource()
    ...


class Law2VecDataSource(BinaryDatasource):
    def fetch_binary(self) -> bytearray:
        pass
#!/usr/bin/python3

# test_data_registry.py
# Date:  19/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from tests.unit.conftest import FakeBinaryDataSource, FakeTabularDataSource


def test_binary_datasource_fetch():
    dummy_data_source = FakeBinaryDataSource()
    assert not dummy_data_source._temporary_file
    data = dummy_data_source.fetch()
    assert dummy_data_source._temporary_file
    assert data == b'Bytes objects are immutable sequences of single bytes'
    assert dummy_data_source.path_to_local_cache().read_bytes() == b'Bytes objects are immutable sequences of single bytes'
    tmp_file = dummy_data_source.path_to_local_cache()
    del dummy_data_source
    assert not tmp_file.exists()


def test_binary_datasource_path():
    dummy_data_source = FakeBinaryDataSource()
    assert not dummy_data_source._temporary_file
    tmp_file = dummy_data_source.path_to_local_cache()
    assert tmp_file.read_bytes() == b'Bytes objects are immutable sequences of single bytes'


def test_tabular_datasource_fetch():
    dummy_data_source = FakeTabularDataSource()
    assert not dummy_data_source._temporary_file
    data = dummy_data_source.fetch()
    assert dummy_data_source._temporary_file
    assert len(data) == 3
    assert len(data.columns) == 3
    assert 'col1' in data.columns
    data2 = dummy_data_source.fetch()
    assert all([x == y for x, y in zip(data.columns, data2.columns)])

#!/usr/bin/python3

# test_eu_cellar.py
# Date:  30/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""

"""
from SPARQLWrapper import SPARQLWrapper

from sem_covid.entrypoints.etl_dags.eurlex import make_request, EURLEX_QUERY, EURLEX_EXTENDED_QUERY


class FakeSPARQL(SPARQLWrapper):
    def __init__(self):
        self._query = 'No query'

    def setQuery(self, query):
        self._query = query

    def setReturnFormat(self, text):
        return True

    def query(self):
        return self

    def convert(self):
        return self._query


def test_sparql_query_make_request_core():
    result = make_request(EURLEX_QUERY, FakeSPARQL())
    assert result


def test_sparql_query_make_request_ext():
    result = make_request(EURLEX_EXTENDED_QUERY, FakeSPARQL())
    assert result

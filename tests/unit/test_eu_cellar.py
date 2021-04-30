#!/usr/bin/python3

# test_eu_cellar.py
# Date:  30/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""

"""
from sem_covid.entrypoints.etl_dags.eurlex_covid19 import make_request, EURLEX_QUERY, EURLEX_EXTENDED_QUERY


def test_sparql_query_make_request_core():
    result = make_request(EURLEX_QUERY)
    assert result


def test_sparql_query_make_request_ext():
    result = make_request(EURLEX_EXTENDED_QUERY)
    assert result

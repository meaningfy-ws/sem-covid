#!/usr/bin/python3

# test_dag_utils.py
# Date:  16/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from sem_covid.entrypoints import dag_name, get_sparql_query, get_index_mapping
from datetime import datetime

from sem_covid.services.index_mapping_registry import IndicesMappingRegistry
from sem_covid.services.sparq_query_registry import QueryRegistry


def test_dag_name():
    assert dag_name(category="a", name="a", role="a",
                    version_major=0, version_minor=0, version_patch=0,
                    versioning=True) == "a_a_a_0.0.0"
    assert dag_name(category="a", name="a", role="a",
                    version_major=0, version_minor=0, version_patch=0,
                    versioning=False) == "a_a_a"
    date_today = datetime.today().strftime('%Y-%m-%d')
    assert dag_name(category="a", name="a", role="a",
                    version_major=None, version_minor=0, version_patch=7,
                    versioning=True) == f"a_a_a_{date_today}(7)"
    assert dag_name(category="a", name="a") == f"a_a_0.1.0"


def test_get_sparql_query():
    q1 = get_sparql_query("cellar_fetcher_generic_metadata.rq")
    assert "SELECT" in q1
    assert "%WORK_ID%" in q1

    q2 = get_sparql_query("cellar_selector_sem_covid_extended.rq")
    assert "SELECT" in q2

    q3 = get_sparql_query("cellar_selector_sem_covid_core.rq")
    assert "SELECT" in q3

    q4 = get_sparql_query("cellar_selector_fin_reg.rq")
    assert "SELECT" in q4

    q5 = get_sparql_query("cellar_selector_legal_initiatives.rq")
    assert "SELECT" in q5


def test_get_sparql_query_registry():
    for query in [QueryRegistry().SEM_COVID_CORE_SELECTOR, QueryRegistry().SEM_COVID_EXTENDED_SELECTOR,
                  QueryRegistry().TREATIES_SELECTOR, QueryRegistry().LEGAL_INITIATIVES_SELECTOR,
                  QueryRegistry().FINANCIAL_REGULATIONS_SELECTOR, QueryRegistry().METADATA_FETCHER]:
        assert "SELECT" in query


def test_get_index_mapping():
    mapping = get_index_mapping("ds_pwdb_mapping.json")
    assert "mappings" in mapping


def test_get_index_mappings():
    for index in [IndicesMappingRegistry().CELLAR_INDEX_MAPPING, IndicesMappingRegistry().PWDB_INDEX_MAPPING,
                  IndicesMappingRegistry().EU_TIMELINE_MAPPING, IndicesMappingRegistry().IRELAND_TIMELINE_MAPPING]:
        assert "mappings" in index

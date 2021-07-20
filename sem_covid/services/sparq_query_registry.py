#!/usr/bin/python3

# sparq_query_registry.py
# Date:  13/07/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    This modules provides an easy access to teh predefined SPARQL queries
    (used, at the time of writing, in the ETL DAGs).
"""
from sem_covid.entrypoints import get_sparql_query


class QueryRegistry:

    @property
    def METADATA_FETCHER(self):
        return get_sparql_query("cellar_fetcher_generic_metadata.rq")

    @property
    def FINANCIAL_REGULATIONS_SELECTOR(self):
        return get_sparql_query("cellar_selector_fin_reg.rq")

    @property
    def LEGAL_INITIATIVES_SELECTOR(self):
        return get_sparql_query("cellar_selector_legal_initiatives.rq")

    @property
    def SEM_COVID_CORE_SELECTOR(self):
        return get_sparql_query("cellar_selector_sem_covid_core.rq")

    @property
    def SEM_COVID_EXTENDED_SELECTOR(self):
        return get_sparql_query("cellar_selector_sem_covid_extended.rq")

    @property
    def TREATIES_SELECTOR(self):
        return get_sparql_query("cellar_selector_treaties.rq")

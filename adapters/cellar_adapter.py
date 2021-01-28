#!/usr/bin/python3

# cellar_adapter.py
# Date:  26/01/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

import logging
from typing import List
from urllib.parse import quote_plus

import requests

logger = logging.getLogger('lam-fetcher')


class CellarAdapter:
    def __init__(self):
        self.url = 'http://publications.europa.eu/webapi/rdf/sparql'
        self.default_graph = ''
        self.format = 'application%2Fsparql-results%2Bjson'
        self.timeout = '0'
        self.debug = 'on'
        self.run = '+Run+Query+'

    def get_celex_ids(self, limit: int = None) -> List[str]:
        """
        Method to retrieve CELEX ids from virtuoso
        :param limit: limit of query results
        :return: CELEX ids
        """
        logger.debug(f'start retrieving {limit} CELEX ids.')
        query = self._limit_query("""prefix cdm: <http://publications.europa.eu/ontology/cdm#>

        select ?celex_id
        where {{
            ?eu_act cdm:resource_legal_id_celex ?celex_id.
            ?eu_act a ?eu_act_type.
            FILTER(?eu_act_type IN (cdm:regulation, cdm:directive, cdm:decision))
        }}""", limit)

        response = self._make_request(query)
        celex_ids = self._extract_values(response, 'celex_id')

        logger.debug(f'finish retrieving {limit} CELEX ids.')
        return celex_ids

    def _make_request(self, query):
        request_url = f'{self.url}/?default-graph-uri={self.default_graph}&format={self.format}&timeout={self.timeout}&debug={self.debug}&run={self.run}&query={quote_plus(query)}'

        response = requests.get(request_url)
        if response.status_code != 200:
            logger.debug(f'request on Virtuoso returned {response.status_code} with {response.content} body')
            raise ValueError(f'request on Virtuoso returned {response.status_code} with {response.content} body')

        return response

    @staticmethod
    def _limit_query(query, limit):
        return query if not limit else query + f' LIMIT {limit}'

    @staticmethod
    def _extract_values(response, key: str):
        return [temp_dict[key]['value'] for temp_dict in response.json()['results']['bindings']]

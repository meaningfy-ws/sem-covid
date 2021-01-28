#!/usr/bin/python3

# search.py
# Date:  15/01/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com 

import logging
from typing import List
from urllib.parse import quote_plus

import requests

logger = logging.getLogger('lam-fetcher')


def get_celex_ids(count: int = 1000) -> List[str]:
    """
    Method to retrieve CELEX ids from virtuoso
    :param count: limit number for the query
    :return: CELEX ids
    """
    logger.debug(f'start retrieving {count} CELEX ids.')
    url = 'http://publications.europa.eu/webapi/rdf/sparql'
    default_graph = ''
    format = 'application%2Fsparql-results%2Bjson'
    timeout = '0'
    debug = 'on'
    run = '+Run+Query+'
    unescaped_query = f"""prefix cdm: <http://publications.europa.eu/ontology/cdm#>

select ?celex_id
where {{
?eu_act cdm:resource_legal_id_celex ?celex_id.
?eu_act a ?eu_act_type.
FILTER(?eu_act_type IN (cdm:regulation, cdm:directive, cdm:decision))
}} LIMIT {count}"""
    request_url = f'{url}/?default-graph-uri={default_graph}&format={format}&timeout={timeout}&debug={debug}&run={run}&query={quote_plus(unescaped_query)}'

    response = requests.get(request_url)
    if response.status_code != 200:
        logger.debug(f'request on Virtuoso returned {response.status_code}')
        raise ValueError(f'request returned {response.status_code}')

    celex_ids = [celex_dict['celex_id']['value'] for celex_dict in response.json()['results']['bindings']]

    logger.debug(f'finish retrieving {count} CELEX ids.')
    return celex_ids

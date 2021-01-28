#!/usr/bin/python3

# cellar_adapter.py
# Date:  26/01/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

import logging
from pathlib import Path
from typing import List
from urllib.parse import quote_plus
from uuid import uuid4

import requests

logger = logging.getLogger('lam-fetcher')

FORMATS = {
    'html': '"application/xhtml+xml" "text/html"',
}


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

    def get_treaties(self) -> dict:
        """
        Method to retrieve works of treaties and their metadata
        :return: dict with metadata
        """
        logger.debug(f'start retrieving works of treaties.')
        query = """prefix cdm: <http://publications.europa.eu/ontology/cdm#>
        select distinct ?work ?doc_id ?comment ?eurovoc_concept ?subject_matter ?directory_code ?date_created ?date_document ?legal_date_signature ?legal_date_entry_into_force ?legal_id_celex ?legal_eli (group_concat(?created_by; separator=", ") as ?authors)
        {
          ?work a cdm:treaty;
                  cdm:work_id_document ?doc_id.
          optional {
            ?work cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/TREATY>
          }
          optional {
            ?work cdm:resource_legal_in-force "true"^^<http://www.w3.org/2001/XMLSchema#boolean>.
          }
          optional {
            ?work cdm:resource_legal_comment_internal ?comment .
          }
          optional {
            ?work cdm:work_is_about_concept_eurovoc ?eurovoc_concept 
          }
          optional {
            ?work cdm:resource_legal_is_about_subject-matter ?subject_matter 
          }
          optional {
            ?work cdm:resource_legal_is_about_concept_directory-code ?directory_code 
          }
          optional {
            ?work cdm:work_created_by_agent ?created_by .
          }
          optional {
            ?work cdm:work_date_creation ?date_created .
          }
          optional {
            ?work cdm:work_date_document ?date_document .
          }
          optional {
            ?work cdm:resource_legal_date_signature ?legal_date_signature .
          }
          optional {
            ?work cdm:resource_legal_date_entry-into-force ?legal_date_entry_into_force .
          }
          optional {
            ?work cdm:resource_legal_id_celex ?legal_id_celex .
          }
          optional {
            ?work cdm:resource_legal_eli ?legal_eli .
          }
          filter not exists{?work a cdm:fragment_resource_legal}.
          filter not exists {?work cdm:work_embargo [].}
        }"""

        response = self._make_request(query)
        return response.json()

    def get_treaty_items(self, treaties: List[str], format='html') -> dict:
        """
        Method to retrieve item for provided treaty works
        :type format: accepted mime types
        :type treaties: list of treaties to run the query against
        :return: dict with metadata
        """
        logger.debug(f'start retrieving items of treaties.')

        query = f"""prefix cdm: <http://publications.europa.eu/ontology/cdm#>
        prefix cmr: <http://publications.europa.eu/ontology/cdm/cmr#>
        prefix lang: <http://publications.europa.eu/resource/authority/language/>
        select distinct ?item ?expressionTitle
        {{
          values ?work {{ {' '.join([f"<{uri}>" for uri in treaties])} }}
          values ?mime {{ {FORMATS[format]} }}
        
          ?expression cdm:expression_belongs_to_work ?work. 
          ?expression cdm:expression_title ?expressionTitle.
          ?expression cdm:expression_uses_language lang:ENG.
          
          ?manifestation cdm:manifestation_manifests_expression ?expression.
        
          ?item cdm:item_belongs_to_manifestation ?manifestation.
          
          ?item cmr:manifestationMimeType ?mime.
        }}
        """

        response = self._make_request(query)
        logger.debug(f'start retrieving items of treaties.')
        return response.json()

    def retrieve_document(self, path_to_save: str, url: str, format: str = 'html'):
        """
        Retrieve document over http to the specified path
        :param path_to_save: location to save file
        :param url: location to retrieve the file from
        :param format: format of the document
        :return: name of the file where the document is retrieved
        """
        logger.debug(f'start retrieving {url} in {format} format.')

        response = requests.get(url)
        if response.status_code != 200:
            logger.debug(f'request on {url} returned {response.status_code} with {response.content}')
            raise ValueError(f'request returned {response.status_code} with {response.content}')

        file_name = str(uuid4()) + f'.{format}'
        file_location = Path(path_to_save) / file_name
        with open(file_location, 'wb') as file:
            file.write(response.content)

        logger.debug(f'finish retrieving {url} in {format} format.')
        return file_name

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
    def _extract_values(dictionary, key: str):
        return [temp_dict[key]['value'] for temp_dict in dictionary['results']['bindings']]

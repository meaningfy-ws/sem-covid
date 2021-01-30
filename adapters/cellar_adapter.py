#!/usr/bin/python3

# cellar_adapter.py
# Date:  26/01/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com
import hashlib
import logging
import os
import pathlib
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
        self.max_query_size = 8000

    def get_treaties(self, limit: int = None) -> dict:
        """
        Method to retrieve works of treaties and their metadata
        :param limit: limit of query results
        :return: dict with metadata
        """
        logger.debug(f'start retrieving works of treaties.')
        query = self._limit_query("""prefix cdm: <http://publications.europa.eu/ontology/cdm#>
        prefix lang: <http://publications.europa.eu/resource/authority/language/>
        
        select distinct ?work ?doc_id ?title ?comment ?eurovocConcept ?subjectMatter ?directoryCode ?dateCreated ?dateDocument ?legalDateSignature ?legalDateEntryIntoForce ?legalIdCelex ?legalEli  group_concat(?createdBy; separator=", ") as ?authors 
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
              ?expression cdm:expression_belongs_to_work ?work. 
              ?expression cdm:expression_title ?title.
              # ?expression cdm:expression_uses_language lang:ENG.
          }
          optional {
            ?work cdm:resource_legal_comment_internal ?comment .
          }
          optional {
            ?work cdm:work_is_about_concept_eurovoc ?eurovocConcept 
          }
          optional {
            ?work cdm:resource_legal_is_about_subject-matter ?subjectMatter 
          }
          optional {
            ?work cdm:resource_legal_is_about_concept_directory-code ?directoryCode 
          }
          optional {
            ?work cdm:work_created_by_agent ?createdBy .
          }
          optional {
            ?work cdm:work_date_creation ?dateCreated .
          }
          optional {
            ?work cdm:work_date_document ?dateDocument .
          }
          optional {
            ?work cdm:resource_legal_date_signature ?legalDateSignature .
          }
          optional {
            ?work cdm:resource_legal_date_entry-into-force ?legalDateEntryIntoForce .
          }
          optional {
            ?work cdm:resource_legal_id_celex ?legalIdCelex .
          }
          optional {
            ?work cdm:resource_legal_eli ?legalEli .
          }
          filter not exists{?work a cdm:fragment_resource_legal}.
          filter not exists {?work cdm:work_embargo [].}
        }""", limit)

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

        query = """prefix cdm: <http://publications.europa.eu/ontology/cdm#>
        prefix cmr: <http://publications.europa.eu/ontology/cdm/cmr#>
        prefix lang: <http://publications.europa.eu/resource/authority/language/>
        select distinct ?item
        {{
          values ?work {{ {values} }}
          values ?mime {{ ~format~ }}
        
          ?expression cdm:expression_belongs_to_work ?work. 
          
          ?manifestation cdm:manifestation_manifests_expression ?expression.
        
          ?item cdm:item_belongs_to_manifestation ?manifestation.
          
          ?item cmr:manifestationMimeType ?mime.
        }}
        """.replace('~format~', FORMATS[format])

        result = {'results': {'bindings': list()}}
        for full_query in self._chunk_query(query, treaties):
            logger.debug('retrieving chunk...')
            response = self._make_request(full_query)
            result['results']['bindings'] += response.json()['results']['bindings']

        logger.debug(f'start retrieving items of treaties.')
        return result

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

    def _chunk_query(self, query: str, values_list: list):
        values_str = ''
        offset = 0
        values_max = self.max_query_size - len(query)

        while values_list[offset:]:
            for value in values_list[offset:]:
                value_to_add = f' <{value}>'
                if len(values_str + value_to_add) >= values_max:
                    break
                values_str += value_to_add
                offset += 1
            print(values_str)
            yield query.format(values=values_str)
            values_str = ''

    def get_covid19_items(self):
        logger.debug(f'start retrieving works of treaties.')
        query = """prefix cdm: <http://publications.europa.eu/ontology/cdm#>
                    prefix lang: <http://publications.europa.eu/resource/authority/language/>
                    
                    SELECT
                    distinct ?title_ 
                    group_concat(distinct ?author; separator=",") as ?authors
                    ?date_document
                    ?celex
                    ?Full_OJ
                    ?manif_pdf
                    ?manif_html
                    ?pdf_to_download
                    ?html_to_download
                    ?oj_sector
                    ?resourceType
                    group_concat(distinct ?eurovocConcept; separator=", ") as ?eurovocConcepts
                    group_concat(distinct ?subjectMatter; separator=", ") as ?subjectMatters
                    group_concat(distinct ?directoryCode; separator=", ") as ?directoryCodes
                    ?legalDateEntryIntoForce
                    group_concat(distinct ?legalEli; separator=", ") as ?legalElis
                    
                    WHERE
                    {
                    ?work cdm:resource_legal_comment_internal ?comment.
                    FILTER(regex(str(?comment),'COVID19'))
                    
                    ?work cdm:work_date_document ?date_document.
                    ?work cdm:work_created_by_agent ?author.
                    ?work cdm:resource_legal_id_celex ?celex.
                    
                      optional {
                        ?work cdm:work_is_about_concept_eurovoc ?eurovocConcept 
                      }
                      optional {
                        ?work cdm:resource_legal_is_about_subject-matter ?subjectMatter 
                      }
                      optional {
                        ?work cdm:resource_legal_is_about_concept_directory-code ?directoryCode 
                      }
                      optional {
                        ?work cdm:resource_legal_date_entry-into-force ?legalDateEntryIntoForce .
                      }
                      optional {
                        ?work cdm:resource_legal_eli ?legalEli .
                      }
                    ?work cdm:resource_legal_id_sector ?oj_sector
                    
                    OPTIONAL
                        {
                            ?work cdm:work_has_resource-type ?resourceType
                        }
                    
                    
                    OPTIONAL
                        {
                            ?work cdm:resource_legal_published_in_official-journal ?Full_OJ.
                        }
                    
                    OPTIONAL
                        {
                            ?exp cdm:expression_title ?title.
                            ?exp cdm:expression_uses_language ?lang.
                            ?exp cdm:expression_belongs_to_work ?work.
                            
                            FILTER(?lang = lang:ENG)
                            OPTIONAL
                            {
                                ?manif_pdf cdm:manifestation_manifests_expression ?exp.
                                ?manif_pdf cdm:manifestation_type ?type_pdf.
                                FILTER(str(?type_pdf) in ('pdf', 'pdfa1a', 'pdfa2a', 'pdfa1b', 'pdfx'))
                            }
                            
                            OPTIONAL
                            {
                                ?manif_html cdm:manifestation_manifests_expression ?exp.
                                ?manif_html cdm:manifestation_type ?type_html.
                                FILTER(str(?type_html) in ('html', 'xhtml'))}}
                                BIND(IF(BOUND(?title),?title,'The title does not exist in that language'@en) as ?title_)
                                BIND(IRI(concat(?manif_pdf,"/zip")) as ?pdf_to_download)
                                BIND(IRI(concat(?manif_html,"/zip")) as ?html_to_download)
                    }
                    
                    order by ?date_document"""

        response = self._make_request(query)
        return response.json()

    def download_covid19_items(self):
        covid19_items = self.get_covid19_items()
        download_location = pathlib.Path('resources/covid19_eurlex')

        count = len(covid19_items['results']['bindings'])
        current_item = 0

        for item in covid19_items['results']['bindings']:
            current_item += 1
            filename = hashlib.sha256(item['title_']['value'].encode('utf-8')).hexdigest()

            filename_pdf = filename + '_pdf.zip'
            filename_html = filename + '_html.zip'

            try:
                print("Processing item " + str(current_item) + " of " + str(count))
                url = item['pdf_to_download']['value'] if item['pdf_to_download']['value'].startswith('http') else (
                        'http://' + item['pdf_to_download']['value'])
                request = requests.get(url, allow_redirects=True)

                with open(pathlib.Path(download_location) / str(filename_pdf), 'wb') as output_file:
                    output_file.write(request.content)

                url = item['html_to_download']['value'] if item['html_to_download']['value'].startswith('http') else (
                        'http://' + item['html_to_download']['value'])
                request = requests.get(url, allow_redirects=True)

                with open(pathlib.Path(download_location) / str(filename_html), 'wb') as output_file:
                    output_file.write(request.content)
            except Exception as ex:
                logger.exception(ex)


    @staticmethod
    def _limit_query(query, limit):
        return query if not limit else query + f' LIMIT {limit}'

    @staticmethod
    def _extract_values(dictionary, key: str):
        return [temp_dict[key]['value'] for temp_dict in dictionary['results']['bindings']]

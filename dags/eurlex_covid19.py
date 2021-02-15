"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
import hashlib
import logging
import os
import pathlib
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

logger = logging.getLogger('lam-fetcher')
version = '0.1'

_url = 'http://publications.europa.eu/webapi/rdf/sparql'
_default_graph = ''
_format = 'application%2Fsparql-results%2Bjson'
_timeout = '0'
_debug = 'on'
_run = '+Run+Query+'
_max_query_size = 8000


def _make_request(query):
    request_url = f'{_url}/?default-graph-uri={_default_graph}&format={_format}&timeout={_timeout}&debug={_debug}&run={_run}&query={quote_plus(query)} '

    response = requests.get(request_url)
    if response.status_code != 200:
        logger.info(f'request on Virtuoso returned {response.status_code} with {response.content} body')
        raise ValueError(f'request on Virtuoso returned {response.status_code} with {response.content} body')

    return response


def get_covid19_items():
    logger.debug(f'Start retrieving EURLex Covid 19 items..')
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

    response = _make_request(query)
    return response.json()


def download_covid19_items(covid19_items, download_location: pathlib.Path = None):
    if download_location is None:
        download_location = pathlib.Path(os.path.dirname(os.path.realpath(__file__))) / pathlib.Path('eurlex')
    logger.info('Enriched fragments will be saved locally to ' + str(download_location))

    count = len(covid19_items['results']['bindings'])
    current_item = 0
    logger.info('Found ' + str(count) + ' EURLex Covid19 items.')

    for item in covid19_items['results']['bindings']:
        current_item += 1
        filename = hashlib.sha256(item['title_']['value'].encode('utf-8')).hexdigest()

        filename_pdf = filename + '_pdf.zip'
        filename_html = filename + '_html.zip'

        try:
            logger.info("Processing item " + str(current_item) + " of " + str(count))
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


def process_eurlex_items():
    covid19_items = get_covid19_items()
    download_covid19_items(covid19_items)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 2, 7),
    "email": ["mclaurentiu79@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=500),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('EURLex_Covid19_DAG_version_' + version, default_args=default_args,
          schedule_interval=timedelta(minutes=1000))

python_task = PythonOperator(task_id='EURLex_Covid19_task_version_' + version,
                             python_callable=process_eurlex_items, retries=1, dag=dag)

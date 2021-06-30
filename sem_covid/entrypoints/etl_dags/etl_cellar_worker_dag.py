
import json
import logging
import tempfile
import hashlib
import zipfile
from tika import parser
from itertools import chain
from pathlib import Path
from sem_covid import config

import requests

from sem_covid.adapters.dag_factory import DagPipeline

from sem_covid.services.store_registry import StoreRegistryManagerABC


logger = logging.getLogger(__name__)


CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'
RESOURCE_FILE_PREFIX = 'res/'
TIKA_FILE_PREFIX = 'tika/'
CONTENT_LANGUAGE = "language"
FIELD_DATA_PREFIX = "works/"


def download_file(source: dict, location_details: str, file_name: str, minio):
    try:
        url = location_details if location_details.startswith('http') \
            else 'http://' + location_details
        request = requests.get(url, allow_redirects=True, timeout=30)
        minio.put_object(RESOURCE_FILE_PREFIX + file_name, request.content)
        source[CONTENT_PATH_KEY].append(file_name)
        return True

    except Exception as e:
        source[FAILURE_KEY] = str(e)
        return False

    # def assert_filename(self, *args, **context):
    #     """
    #      Fail hard if no filename is provided=.
    #     """
    #     if "filename" not in context['dag_run'].conf:
    #         message = "Could not find the file name in the provided configuration. " \
    #                   "This DAG is to be triggered by its parent only."
    #         logger.error(message)
    #         raise ValueError(message)


class CellarDagWorker(DagPipeline):

    def __init__(self, sparql_query: str, sparql_url: str, minio_bucket_name: str, store_registry: StoreRegistryManagerABC):
        self.store_registry = store_registry
        self.minio_bucket_name = minio_bucket_name
        self.sparql_query = sparql_query
        self.sparql_url = sparql_url

    def get_steps(self) -> list:
        return [self.download_documents_and_enrich_json,
                self.extract_content_with_tika,
                self.content_cleanup,
                self.upload_to_elastic
                ]

    def download_documents_and_enrich_json(self, **context):
        if "work" not in context['dag_run'].conf:
            logger.error(
                "Could not find the work in the provided configuration. This DAG is to be triggered by its parent only.")
            return

        work = context['dag_run'].conf['work']
        logger.info(f'Enriched fragments will be saved locally to the bucket {config.EU_FINREG_CELLAR_BUCKET_NAME}')

        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        json_filename = FIELD_DATA_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
        json_content = self.store_registry.sparql_triple_store(self.sparql_url).with_query(
            sparql_query=self.sparql_query.replace("%WORK_ID%", work)).get_dataframe().to_dict()

        json_content[CONTENT_PATH_KEY] = list()
        if json_content.get('manifs_html'):
            for html_manifestation in json_content.get('htmls_to_download'):
                filename = hashlib.sha256(html_manifestation.encode('utf-8')).hexdigest()

                logger.info(f"Downloading HTML manifestation for {(json_content['title'] or json_content['work'])}")

                html_file = filename + '_html.zip'
                download_file(json_content, html_manifestation, html_file, minio)
        elif json_content.get('manifs_pdf'):
            for pdf_manifestation in json_content.get('pdfs_to_download'):

                filename = hashlib.sha256(pdf_manifestation.encode('utf-8')).hexdigest()

                logger.info(f"Downloading PDF manifestation for {(json_content['title'] or json_content['work'])}")

                pdf_file = filename + '_pdf.zip'
                download_file(json_content, pdf_manifestation, pdf_file, minio)
        else:
            logger.warning(f"No manifestation has been found for {(json_content['title'] or json_content['work'])}")

        minio.put_object(json_filename, json.dumps(json_content))


    def extract_content_with_tika(self, **context):
        if "work" not in context['dag_run'].conf:
            logger.error(
                "Could not find the work in the provided configuration. This DAG is to be triggered by its parent only.")
            return

        work = context['dag_run'].conf['work']
        json_file_name = FIELD_DATA_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
        logger.info(f'Using Apache Tika at {config.APACHE_TIKA_URL}')
        logger.info(f'Loading resource files from {json_file_name}')
        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        json_content = json.loads(minio.get_object(json_file_name))

        counter = {
            'general': 0,
            'success': 0
        }

        valid_sources = 0
        identifier = json_content['work']
        logger.info(f'Processing {identifier}')
        json_content[CONTENT_KEY] = list()

        if FAILURE_KEY in json_content:
            logger.info(
                f'Will not process source <{identifier}> because it failed download with reason <{json_content[FAILURE_KEY]}>')
        else:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    for content_path in json_content[CONTENT_PATH_KEY]:
                        current_zip_location = Path(temp_dir) / Path(content_path)
                        with open(current_zip_location, 'wb') as current_zip:
                            content_bytes = bytearray(minio.get_object(RESOURCE_FILE_PREFIX + content_path))
                            current_zip.write(content_bytes)
                        with zipfile.ZipFile(current_zip_location, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)

                        logger.info(f'Processing each file from {content_path}:')
                        for content_file in chain(Path(temp_dir).glob('*.html'), Path(temp_dir).glob('*.pdf')):
                            logger.info(f'Parsing {Path(content_file).name}')
                            parse_result = parser.from_file(str(content_file), config.APACHE_TIKA_URL)

                            if 'content' in parse_result:
                                json_content[CONTENT_KEY].append(parse_result['content'])
                                json_content[CONTENT_LANGUAGE] = (
                                        parse_result["metadata"].get("Content-Language")
                                        or
                                        parse_result["metadata"].get("content-language")
                                        or
                                        parse_result["metadata"].get("language"))

                                valid_sources += 1
                            else:
                                logger.warning(
                                    f'Apache Tika did NOT return a valid content for the source {Path(content_file).name}')
                        json_content[CONTENT_KEY] = " ".join(json_content[CONTENT_KEY])
            except Exception as e:
                logger.exception(e)

        minio.put_object(json_file_name, json.dumps(json_content))

        logger.info(f"Parsed a total of {counter['general']} files, of which successfully {counter['success']} files.")
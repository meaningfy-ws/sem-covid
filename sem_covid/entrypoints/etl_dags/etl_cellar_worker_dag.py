import json
import logging
import tempfile
import hashlib
import zipfile
from typing import List, Tuple

from tika import parser
from itertools import chain
from pathlib import Path
from sem_covid import config
import re

import requests

from sem_covid.adapters.abstract_store import ObjectStoreABC
from sem_covid.adapters.dag_factory import DagPipeline
from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import DOCUMENTS_PREFIX, RESOURCE_FILE_PREFIX
from sem_covid.services.sc_wrangling.data_cleaning import clean_fix_unicode, clean_to_ascii, clean_remove_line_breaks

from sem_covid.services.store_registry import StoreRegistryManagerABC

logger = logging.getLogger(__name__)

CONTENT_PATH_KEY = 'content_path'
CONTENT_KEY = 'content'
FAILURE_KEY = 'failure_reason'
TIKA_FILE_PREFIX = 'tika/'
CONTENT_LANGUAGE = "language"
DOWNLOAD_TIMEOUT = 30


def download_manifestation_file(source_location: str, minio: ObjectStoreABC, source_type: str = "html",
                                prefix: str = RESOURCE_FILE_PREFIX) -> str:
    """
        Download the source_location to object store and return the file path
    """
    logger.info(f"Downloading the {source_type} manifestation from {source_location}")
    download_url = source_location if source_location.startswith('http') else 'http://' + source_location
    request = requests.get(download_url, allow_redirects=True, timeout=DOWNLOAD_TIMEOUT)
    download_file_path = prefix + hashlib.sha256(source_location.encode('utf-8')).hexdigest() + \
                         "_" + source_type + ".zip"
    minio.put_object(download_file_path, request.content)
    logger.info(f"Downloaded successfully the {source_type} manifestation from {source_location} "
                f"and saved it as {download_file_path}")
    return download_file_path


def get_work_uri_from_context(*args, **context):
    """
     Fail hard if no work URI is provided in the context
    """
    if ("conf" not in context['dag_run']) or ("work" not in context['dag_run']['conf']):
        message = "Could not find the work URI in the provided document. " \
                  "This DAG is to be triggered by its parent only."
        logger.error(message)
        raise ValueError(message)
    return context['dag_run']["conf"]['work']


def content_cleanup_tool(text: str) -> str:
    """
        Perform teh text cleanup and return teh results
    """
    result = text
    result = clean_fix_unicode(result)
    result = clean_to_ascii(result)
    result = re.sub(r"\s+", " ", result)
    result = clean_remove_line_breaks(result)

    return result


def download_zip_objects_to_temp_folder(object_paths: List[str], minio_client: ObjectStoreABC):
    """
        download the zip objects from an object store and
        extract the zip content into a temporary folder
    """
    temp_dir = tempfile.mkdtemp(prefix="cellar_dag_")
    for content_path in object_paths:
        current_zip_location = Path(temp_dir) / str(content_path)
        with open(current_zip_location, 'wb') as current_zip:
            content_bytes = bytearray(minio_client.get_object(content_path))
            current_zip.write(content_bytes)
        with zipfile.ZipFile(current_zip_location, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    return temp_dir


def select_relevant_files_from_temp_folder(temp_folder):
    return list(chain(Path(temp_folder).glob('*.html'),
                      Path(temp_folder).glob('*.xml'),
                      Path(temp_folder).glob('*.xhtml'),
                      Path(temp_folder).glob('*.doc'),
                      Path(temp_folder).glob('*.docx'),
                      Path(temp_folder).glob('*.pdf')))


def get_text_from_selected_files(list_of_file_paths: List[str], tika_service_url: str = config.APACHE_TIKA_URL) \
        -> List[Tuple[str, str]]:
    """
        for a given list of file paths,
        read the files and pass them one by one to Tika
        collect the results and return the list of content dicts with (file_name, file_content, content_language) provided

        return:  list of content dicts with (file_name, file_content, content_language) provided
    """
    # TODO:
    ...


class CellarDagWorker(DagPipeline):

    def __init__(self, sparql_query: str, sparql_url: str, minio_bucket_name: str,
                 store_registry: StoreRegistryManagerABC):
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
        """
            This function
            (0) reads the work document from minio if one exist
            (1) queries the Cellar for all the metadata for a given Work URI
            (2) downloads all the manifestations (returned by the query)
            (3) store the paths to the downloaded manifestations in the work document (json in Minio).
        """

        work = get_work_uri_from_context(**context)
        logger.info(
            f'Fetching metadata and manifestations for {work}. The content will be saved to {self.minio_bucket_name} bucket.')
        minio = self.store_registry.minio_object_store(self.minio_bucket_name)

        work_document_filename = DOCUMENTS_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
        work_document_content = json.loads(minio.get_object(object_name=work_document_filename).decode('utf-8'))

        assert isinstance(work_document_content, dict), "The work document must be a dictionary"

        work_metadata = self.store_registry.sparql_triple_store(self.sparql_url).with_query(
            sparql_query=self.sparql_query.replace("%WORK_ID%", work)).get_dataframe().to_dict(orient="records")

        # we expect that there will be work one set of metadata,
        # otherwise makes no sense to continue
        if isinstance(work_metadata, list) and len(work_metadata) > 0:
            work_document_content.update(work_metadata[0])
        elif isinstance(work_metadata, dict):
            work_document_content.update(work_metadata)
        else:
            raise ValueError(f"No metadata were found for {work} work")

        list_of_downloaded_manifestation_object_paths = []
        if work_document_content.get('htmls_to_download'):
            # ensuring we always iterate trough a list
            htmls_to_download = work_document_content.get('htmls_to_download') \
                if isinstance(work_document_content.get('htmls_to_download'), list) \
                else [work_document_content.get('htmls_to_download')]
            for html_manifestation in htmls_to_download:
                list_of_downloaded_manifestation_object_paths.append(
                    download_manifestation_file(source_location=html_manifestation,
                                                minio=minio,
                                                prefix=RESOURCE_FILE_PREFIX,
                                                source_type="html"))
        elif work_document_content.get('pdfs_to_download'):
            # ensuring we always iterate trough a list
            pdfs_to_download = work_document_content.get('pdfs_to_download') \
                if isinstance(work_document_content.get('pdfs_to_download'), list) \
                else [work_document_content.get('pdfs_to_download')]
            for pdf_manifestation in pdfs_to_download:
                list_of_downloaded_manifestation_object_paths.append(
                    download_manifestation_file(source_location=pdf_manifestation,
                                                minio=minio,
                                                prefix=RESOURCE_FILE_PREFIX,
                                                source_type="pdf"))
        else:
            logger.warning(f"No manifestation has been found for {work}")

        # enriching the document with a list of paths to downloaded manifestations
        work_document_content[CONTENT_PATH_KEY] = list_of_downloaded_manifestation_object_paths
        minio.put_object(work_document_filename, json.dumps(work_document_content))

    def extract_content_with_tika(self, **context):
        """
            This function:
            - for each work manifestation zip
               (1) extract all the files from the zip and
               (2) pass each file through Tika service and
               (3) the free text output is concatenated and
               (4) injected into the work document and
               (5) the updated work document is stored in object store
        """
        work = get_work_uri_from_context(**context)
        json_file_name = DOCUMENTS_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
        # logger.info(f'Using Apache Tika at {config.APACHE_TIKA_URL}')

        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        json_content = json.loads(minio.get_object(json_file_name))
        logger.info(f'Loaded the work document JSON from {json_file_name}')

        # download archives and unzip them
        list_of_downloaded_manifestation_object_paths = [RESOURCE_FILE_PREFIX + content_path for content_path in
                                                         json_content[CONTENT_KEY]]
        temp_folder = download_zip_objects_to_temp_folder(object_paths=list_of_downloaded_manifestation_object_paths,
                                                          minio_client=minio)
        # select relevant files and pass them through Tika
        list_of_selected_files = select_relevant_files_from_temp_folder(temp_folder)
        file_content_tuples = get_text_from_selected_files(list_of_file_paths=list_of_selected_files,
                                                           tika_service_url=config.APACHE_TIKA_URL)

        # merge results from Tika into a unified work content
        # TODO:
        ...

        # logger.info(f'Processing {work}')
        json_content[CONTENT_KEY] = list()
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
                    for content_file in chain(Path(temp_dir).glob('*.html'), Path(temp_dir).glob('*.xml'),
                                              Path(temp_dir).glob('*.pdf')):
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
                        else:
                            logger.warning(
                                f'Apache Tika did NOT return a valid content for the source {Path(content_file).name}')
                    json_content[CONTENT_KEY] = " ".join(json_content[CONTENT_KEY])
        except Exception as e:
            logger.exception(e)

        # if FAILURE_KEY in json_content:
        #     logger.info(
        #         f'Will not process source <{work}> because it failed download with reason <{json_content[FAILURE_KEY]}>')
        # else:
        #     try:
        #         with tempfile.TemporaryDirectory() as temp_dir:
        #             for content_path in json_content[CONTENT_PATH_KEY]:
        #                 current_zip_location = Path(temp_dir) / Path(content_path)
        #                 with open(current_zip_location, 'wb') as current_zip:
        #                     content_bytes = bytearray(minio.get_object(RESOURCE_FILE_PREFIX + content_path))
        #                     current_zip.write(content_bytes)
        #                 with zipfile.ZipFile(current_zip_location, 'r') as zip_ref:
        #                     zip_ref.extractall(temp_dir)
        #
        #                 logger.info(f'Processing each file from {content_path}:')
        #                 for content_file in chain(Path(temp_dir).glob('*.html'), Path(temp_dir).glob('*.xml'),
        #                                           Path(temp_dir).glob('*.pdf')):
        #                     logger.info(f'Parsing {Path(content_file).name}')
        #                     parse_result = parser.from_file(str(content_file), config.APACHE_TIKA_URL)
        #
        #                     if 'content' in parse_result:
        #                         json_content[CONTENT_KEY].append(parse_result['content'])
        #                         json_content[CONTENT_LANGUAGE] = (
        #                                 parse_result["metadata"].get("Content-Language")
        #                                 or
        #                                 parse_result["metadata"].get("content-language")
        #                                 or
        #                                 parse_result["metadata"].get("language"))
        #                     else:
        #                         logger.warning(
        #                             f'Apache Tika did NOT return a valid content for the source {Path(content_file).name}')
        #                 json_content[CONTENT_KEY] = " ".join(json_content[CONTENT_KEY])
        #     except Exception as e:
        #         logger.exception(e)

        minio.put_object(json_file_name, json.dumps(json_content))

    def content_cleanup(self, *args, **context):
        """
            This function will clean the content of the document from minio
        """
        work = get_work_uri_from_context(**context)
        json_file_name = DOCUMENTS_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"

        logger.info(f'Cleaning up the the fragment {json_file_name}')
        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        document = json.loads(minio.get_object(json_file_name).decode('utf-8'))

        if "content" in document and document["content"]:
            document["content"] = content_cleanup_tool(document["content"])

            minio.put_object(json_file_name, json.dumps(document))
            logger.info(
                f"Completed cleanup on {json_file_name} titled {document['title']} workID {document['work']}")
        else:
            logger.warning(
                f"Skipping a fragment without content {json_file_name} titled {document['title']} workID {document['work']}")

    def upload_to_elastic(self, *args, **context):
        work = get_work_uri_from_context(**context)
        json_file_name = DOCUMENTS_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"
        es_adapter = self.store_registry.es_index_store()
        logger.info(f'Using ElasticSearch at {config.ELASTICSEARCH_HOST_NAME}:{config.ELASTICSEARCH_PORT}')

        logger.info(f'Loading files from {config.MINIO_URL}')

        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        json_content = json.loads(minio.get_object(json_file_name).decode('utf-8'))
        try:
            logger.info(
                f'Sending to ElasticSearch ( {config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME} ) the file {json_file_name}')
            es_adapter.index(index_name=config.EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                             document_id=json_file_name.split("/")[1],
                             document_body=json_content)
        except Exception:
            logger.exception("Could not upload to Elasticsearch")

        logger.info(f'Sent {json_file_name} file(s) to ElasticSearch successfully.')

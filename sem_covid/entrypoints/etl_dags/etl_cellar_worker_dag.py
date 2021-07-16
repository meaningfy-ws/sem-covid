import hashlib
import json
import logging
import re
import tempfile
import zipfile
from itertools import chain
from pathlib import Path
from typing import List

import pandas as pd
import requests
from tika import parser

from sem_covid import config
from sem_covid.adapters.abstract_store import ObjectStoreABC
from sem_covid.adapters.dag.base_etl_dag_pipeline import BaseETLPipeline
from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import DOCUMENTS_PREFIX, RESOURCE_FILE_PREFIX, CONTENT_KEY, \
    CONTENT_LANGUAGE, CONTENT_PATH_KEY, DOWNLOAD_TIMEOUT, get_documents_from_triple_store, WORK_ID_COLUMN
from sem_covid.services.sc_wrangling.data_cleaning import clean_fix_unicode, clean_to_ascii, clean_remove_line_breaks
from sem_covid.services.store_registry import StoreRegistryABC

logger = logging.getLogger(__name__)


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
    if WORK_ID_COLUMN not in context['dag_run'].conf:
        message = "Could not find the work URI in the provided document. " \
                  "This DAG is to be triggered by its parent only."
        logger.error(message)
        raise ValueError(message)
    return context['dag_run'].conf[WORK_ID_COLUMN]


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
        current_zip_location.parent.mkdir(parents=True, exist_ok=True)
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


def get_text_from_selected_files(list_of_file_paths: List[Path], tika_service_url: str = config.APACHE_TIKA_URL) \
        -> List:
    """
        for a given list of file paths,
        read the files and pass them one by one to Tika
        collect the results and return the list of content dicts with (file_content, content_language) provided

        return:  list of content dicts with (file_content, content_language) provided
    """
    list_of_dictionaries = []
    for file_path in list_of_file_paths:
        content_dictionary = {}
        # Sending file to tika for parsing. The return result will be a dictionary
        parse_result = parser.from_file(str(file_path), tika_service_url)
        # extracting the content and language from the returned dictionary from TIKA
        content_dictionary[CONTENT_KEY] = parse_result[CONTENT_KEY]
        languages = {
            parse_result["metadata"].get("Content-Language"),
            parse_result["metadata"].get("content-language"),
            parse_result["metadata"].get("language")}
        content_dictionary[CONTENT_LANGUAGE] = languages.pop()
        list_of_dictionaries.append(content_dictionary)
    return list_of_dictionaries


class CellarDagWorker(BaseETLPipeline):
    """
        A generic worker pipeline for getting a Work document from cellar (based on Work URI)
    """

    def __init__(self, sparql_query: str, sparql_endpoint_url: str, minio_bucket_name: str, index_name: str,
                 store_registry: StoreRegistryABC):
        self.store_registry = store_registry
        self.minio_bucket_name = minio_bucket_name
        self.sparql_query = sparql_query
        self.sparql_endpoint_url = sparql_endpoint_url
        self.index_name = index_name

    def extract(self, **context):
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

        work_metadata_df = get_documents_from_triple_store(
            list_of_queries=[self.sparql_query.replace("%WORK_ID%", work)],
            list_of_query_flags=["metadata"],
            triple_store_adapter=self.store_registry.sparql_triple_store(self.sparql_endpoint_url),
            id_column=WORK_ID_COLUMN)

        logger.info(f"Head of teh raw metadata {work_metadata_df.iloc[0]}")

        # work_metadata_df.where(cond=work_metadata_df.notnull(), other=None, inplace=True)
        work_metadata = work_metadata_df.to_dict(orient="records")
        logger.info(
            f"Found work document ({type(work_document_content)}) {work_document_content}")
        # we expect that there will be work one set of metadata,
        # otherwise makes no sense to continue
        if isinstance(work_metadata, list) and len(work_metadata) > 0:
            work_metadata = work_metadata[0]
        else:
            raise ValueError(f"No metadata were found for {work} work")
        logger.info(
            f"Enriching work document content with fetched metadata  ({type(work_metadata)}) {work_metadata}")
        work_document_content.update(work_metadata)

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

        # Pandas dataframe needs to have
        logger.info(f"List of downloaded manifestations paths {list_of_downloaded_manifestation_object_paths}")
        list_of_downloaded_manifestation_object_paths = list_of_downloaded_manifestation_object_paths \
            if list_of_downloaded_manifestation_object_paths else None
        # enriching the document with a list of paths to downloaded manifestations
        work_document_content[CONTENT_PATH_KEY] = list_of_downloaded_manifestation_object_paths
        minio.put_object(work_document_filename, json.dumps(work_document_content))

    def transform_structure(self, **context):
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
        # list_of_downloaded_manifestation_object_paths = [RESOURCE_FILE_PREFIX + content_path for content_path in
        #                                                  json_content[CONTENT_PATH_KEY]]
        list_of_downloaded_manifestation_object_paths = [content_path for content_path in
                                                         json_content[CONTENT_PATH_KEY]]
        temp_folder = download_zip_objects_to_temp_folder(object_paths=list_of_downloaded_manifestation_object_paths,
                                                          minio_client=minio)
        # select relevant files and pass them through Tika
        list_of_selected_files = select_relevant_files_from_temp_folder(temp_folder)
        file_content_dictionaries = get_text_from_selected_files(list_of_file_paths=list_of_selected_files,
                                                                 tika_service_url=config.APACHE_TIKA_URL)

        # merge results from Tika into a unified work content
        logger.info(f"List of content dictionaries = {len(file_content_dictionaries)}")
        # The content is concatenated into a single string and we have a single language
        json_content[CONTENT_KEY] = ". ".join([dictionary[CONTENT_KEY] for dictionary in file_content_dictionaries])
        languages = set([dictionary[CONTENT_LANGUAGE] for dictionary in file_content_dictionaries])
        json_content[CONTENT_LANGUAGE] = languages.pop() if languages else None

        # for dictionary in file_content_dictionaries:
        #     json_content[CONTENT_KEY].append(dictionary[CONTENT_KEY])
        #     json_content[CONTENT_LANGUAGE].append(dictionary[CONTENT_LANGUAGE])
        # json_content[CONTENT_KEY] = " ".join(json_content[CONTENT_KEY])
        # json_content[CONTENT_LANGUAGE] = str(json_content[CONTENT_LANGUAGE][0])
        # update work document in object store
        minio.put_object(json_file_name, json.dumps(json_content))

    def transform_content(self, *args, **context):
        """
            This function will clean the content of the document from minio
        """
        work = get_work_uri_from_context(**context)
        json_file_name = DOCUMENTS_PREFIX + hashlib.sha256(work.encode('utf-8')).hexdigest() + ".json"

        logger.info(f'Cleaning up the the fragment {json_file_name}')
        minio = self.store_registry.minio_object_store(self.minio_bucket_name)
        document = json.loads(minio.get_object(json_file_name).decode('utf-8'))

        if CONTENT_KEY in document and document[CONTENT_KEY]:
            document[CONTENT_KEY] = content_cleanup_tool(document[CONTENT_KEY])

            minio.put_object(json_file_name, json.dumps(document))
            logger.info(
                f"Completed cleanup on {json_file_name} workID {document[WORK_ID_COLUMN]}")
        else:
            logger.warning(
                f"Skipping a fragment without content {json_file_name} workID {document[WORK_ID_COLUMN]}")

    def load(self, *args, **context):
        work = get_work_uri_from_context(**context)
        document_id = hashlib.sha256(work.encode('utf-8')).hexdigest()
        json_file_name = DOCUMENTS_PREFIX + document_id + ".json"
        es_adapter = self.store_registry.es_index_store()
        minio = self.store_registry.minio_object_store(self.minio_bucket_name)

        logger.info(f'Processing Work {work} from json_file {json_file_name}')
        json_content = json.loads(minio.get_object(json_file_name).decode('utf-8'))
        json_content = [json_content] if isinstance(json_content, dict) else json_content
        document_df = pd.DataFrame.from_records(data=json_content, index=[document_id])
        logger.info(
            f'Using ElasticSearch at {config.ELASTICSEARCH_HOST_NAME}:{config.ELASTICSEARCH_PORT}')

        logger.info(
            f'Sending to ElasticSearch ( {self.index_name} ) the file {json_file_name}')

        es_adapter.put_dataframe(index_name=self.index_name,
                                 content=document_df)
        # es_adapter.index(index_name=config.LEGAL_INITIATIVES_ELASTIC_SEARCH_INDEX_NAME,
        #                  document_id=json_file_name.split("/")[1],
        #                  document_body=json_content)

        logger.info(f'Sent {json_file_name} file(s) to ElasticSearch successfully.')

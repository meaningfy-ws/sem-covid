import hashlib
import io

import pytest
from pathlib import Path
import tempfile
import zipfile

from sem_covid import config
from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import DOCUMENTS_PREFIX, RESOURCE_FILE_PREFIX
from sem_covid.entrypoints.etl_dags.etl_cellar_worker_dag import download_manifestation_file, CellarDagWorker, \
    get_work_uri_from_context
from sem_covid.services.store_registry import StoreRegistry
from tests.unit.test_store.fake_store_registry import FakeStoreRegistryManager

QUERY = "sparql query"
SPARQL_URL = "www.fake.com"
MINIO_BUCKET_NAME = "fake_bucket"
store_registry = FakeStoreRegistryManager()


def test_download_manifestation_file():
    """
        assert that
        * the content is downloaded (not null)
        * the return is the filename in minio
        * the content is saved in minio
    """
    source_url = 'https://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1.0006.03/DOC_1'
    minio_client = store_registry.minio_object_store('fake_bucket')

    download_file_path = download_manifestation_file(source_url, minio_client)
    assert len(minio_client.list_objects(RESOURCE_FILE_PREFIX)) == 1
    assert download_file_path == 'res/469dd24712ac3f7bb71e3435c0ba9224cc0676b0f2a6508279ce8d9b5d122778_html.zip'


def test_get_work_uri_from_context():
    context1 = {}
    context = {"dag_run": {
        "conf": {"work": "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"}}}
    response = get_work_uri_from_context(**context)
    assert response == "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"
    with pytest.raises(KeyError):
        # we test that the work uri is not in the context
        get_work_uri_from_context()


def test_download_documents_and_enrich_json():
    """
        assert that:
        * metadata exists (was queried from cellar)
        * manifestation object paths exists in teh work document
        * manifestations exist in min io (objects exist in minio)
    """
    # instantiating the class
    json_file_name = DOCUMENTS_PREFIX + hashlib.sha256(
        "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"
            .encode('utf-8')).hexdigest() + ".json"
    minio_client = store_registry.minio_object_store('fake_bucket')
    minio_client.put_object(json_file_name, b'{}')

    context = {"dag_run": {
        "conf": {"work": "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"}}}

    worker_dag = CellarDagWorker(QUERY, SPARQL_URL, MINIO_BUCKET_NAME, store_registry)
    worker_dag.download_documents_and_enrich_json(**context)

    assert len(minio_client.list_objects(object_name_prefix=RESOURCE_FILE_PREFIX)) > 0

    with pytest.raises(KeyError):
        # we test that the work uri is not in the context
        worker_dag.download_documents_and_enrich_json()


def test_download_zip_objects_to_temp_folder():
    """
        store a zip in the fake object store
        pass the path to the test function
        assert that the extracted content is in the returned temp folder
    """
    # TODO:
    ...

# def test_extract_content_with_tika(fragment1_eu_cellar_covid):
#     CONTENT_PATH_KEY = 'content_path'
#     json_content = fragment1_eu_cellar_covid
#     minio_client = store_registry.minio_object_store('fake_bucket').put_object("one", json_content)
#     content_bytes = store_registry.minio_object_store('fake_bucket').get_object("one")
#     # print(content_bytes)
#     for content_path in json_content[CONTENT_PATH_KEY]:
#
#         print(content_path)

# def test_file_from_minio():
#     RESOURCE_FILE_PREFIX = 'res/'
#     minio = StoreRegistry.minio_object_store(config.EU_FINREG_CELLAR_BUCKET_NAME)
#     object = bytearray(minio.get_object(RESOURCE_FILE_PREFIX + "f51f4096ab20fba0467877e3109ef5457bfb078f5d709552055d9f634b335009_html.zip"))
#
#     unzip=zipfile.ZipFile(io.BytesIO(object))
#     print(unzip.open())
#
#     # with zipfile.ZipFile(object, "r") as zip_ref:
#     #     content = zip_ref.extract()
#     # print(content)
#
#     # with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
#     #     zip_ref.extractall(directory_to_extract_to)

def test_content_cleanup(fragment3_eu_cellar_covid):
    work_uri = "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"
    # json_file_name = DOCUMENTS_PREFIX + hashlib.sha256(work_uri.encode('utf-8')).hexdigest() + ".json"

    store_registry.minio_object_store('fake_bucket').put_object("json_file_name", fragment3_eu_cellar_covid)
    worker_dag = CellarDagWorker(QUERY, SPARQL_URL, MINIO_BUCKET_NAME, store_registry)
    context1 = {}
    context = {"dag_run": {"conf": {"work": work_uri}}}

    worker_dag.content_cleanup(**context)

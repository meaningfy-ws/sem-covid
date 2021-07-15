import hashlib
import io
import pathlib
import re

import pandas as pd
import pytest
from pathlib import Path
import tempfile
import zipfile

from sem_covid import config
from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import DOCUMENTS_PREFIX, RESOURCE_FILE_PREFIX
from sem_covid.entrypoints.etl_dags.etl_cellar_worker_dag import download_manifestation_file, CellarDagWorker, \
    get_work_uri_from_context, content_cleanup_tool, select_relevant_files_from_temp_folder, \
    download_zip_objects_to_temp_folder, get_text_from_selected_files
from sem_covid.services.store_registry import StoreRegistry
from tests.unit.test_store.fake_storage import FakeObjectStore
from tests.unit.test_store.fake_store_registry import FakeStoreRegistry

QUERY = "sparql query"
SPARQL_URL = "www.fake.com"
MINIO_BUCKET_NAME = "fake_bucket"
store_registry = FakeStoreRegistry()
object_store = FakeObjectStore()


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

# TODO refactor this test
# def test_get_work_uri_from_context():
#     context1 = {}
#     context = {"dag_run": {
#         "conf": {"work": "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"}}}
#     response = get_work_uri_from_context(**context)
#     assert response == "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"
#     with pytest.raises(KeyError):
#         # we test that the work uri is not in the context
#         get_work_uri_from_context()


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
    worker_dag.extract(**context)

    assert len(minio_client.list_objects(object_name_prefix=RESOURCE_FILE_PREFIX)) > 0

    with pytest.raises(KeyError):
        # we test that the work uri is not in the context
        worker_dag.extract()


# TODO, implement the commented tests
# def test_download_zip_objects_to_temp_folder():
#     """
#         store a zip in the fake object store
#         pass the path to the test function
#         assert that the extracted content is in the returned temp folder
#     """
#     path_to_zip_file = pathlib.Path(__file__).parent.parent / "test_data" / "test_zip" / "test.zip"
#     zipfile = str(path_to_zip_file.read_bytes())
#     minio_client = store_registry.minio_object_store('fake_bucket')
#     minio_client.put_object(object_name="test", content=zipfile)
#     print(minio_client._objects)
#     zip_extractor = download_zip_objects_to_temp_folder(["test"], object_store)
#     print (zip_extractor)
#
#
# def test_get_text_from_selected_files(fragment1_eu_cellar_covid):
#     """
#         from a list of file paths
#         get back a list of dictionaries with content and language keys
#     """
#     list_path = [fragment1_eu_cellar_covid]
#     # text_grabber = get_text_from_selected_files(list_path)


def test_select_relevant_files_from_temp_folder():
    temp_dir = pathlib.Path(__file__).parent.parent.parent / "test_data" / "test_folder"
    list_of_files_from_folder = select_relevant_files_from_temp_folder(temp_dir)

    assert list == type(list_of_files_from_folder)
    assert len(list_of_files_from_folder) == 2
    for file in list_of_files_from_folder:
        assert file.exists()


# def test_extract_content_with_tika(fragment1_eu_cellar_covid):
#     CONTENT_PATH_KEY = 'content_path'
#     json_content = fragment1_eu_cellar_covid
#     minio_client = store_registry.minio_object_store('fake_bucket').put_object("one", json_content)
#     content_bytes = store_registry.minio_object_store('fake_bucket').get_object("one")
#     # print(content_bytes)
#
#     # worker_dag = CellarDagWorker(QUERY, SPARQL_URL, MINIO_BUCKET_NAME, store_registry)
#     # worker_dag.extract_content_with_tika()
#
#     for content_path in json_content[CONTENT_PATH_KEY]:
#
#         print(type(content_path))

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


def test_content_cleanup_tool(fragment3_eu_cellar_covid):
    content = content_cleanup_tool(fragment3_eu_cellar_covid["content"])
    assert "\n" not in content
    assert "á" not in content
    assert "—" not in content
    assert "\u2014" not in content
    assert b"\u2014".decode("utf-8") not in content
    assert not re.match(r"\s\s", content)

# def test_zip():
#     object_paths = ["res/3eb4e21d5ecf9e5ffaf57fc45b9815fab3bdff59a5b650185eb6231513595eb5_html.zip"]
#
#     temp_dir = tempfile.mkdtemp(prefix="cellar_dag_")
#     for content_path in object_paths:
#         current_zip_location = Path(temp_dir) / str(content_path)
#         current_zip_location.parent.mkdir(parents=True, exist_ok=True)
#         with open(current_zip_location, 'wb') as current_zip:
#             content_bytes = bytearray("hello world".encode())
#             current_zip.write(content_bytes)
#         with zipfile.ZipFile(current_zip_location, 'r') as zip_ref:
#             zip_ref.extractall(temp_dir)

# def test_apend_dict():
#     json_content = {
#         "work": "http://publications.europa.eu/resource/cellar/1b0572d2-d1f3-11e8-9424-01aa75ed71a1",
#         "title": "COMMISSION DELEGATED REGULATION (EU) …/.. and presentation",
#         "cdm_types": "http://publications.europa.eu/ontology/cdm#work",
#
#         "core":
#             [
#                 "true"
#             ],
#         "eu_cellar_core": "null",
#         "eu_cellar_extended": "null",
#         "content_path":
#             [
#                 "res/3ebbf43df528d345ba63f0556afd8fb09e4c8b4126bba4d7a7af280c2b81018a_html.zip"
#             ]
#     }
#     CONTENT_KEY = "content"
#     CONTENT_LANGUAGE = "language"
#     json_content[CONTENT_KEY] = list()
#     json_content[CONTENT_LANGUAGE] = list()
#
#     file_content_dictionaries = [{"content": "hello from", "language": "en"},
#                                  {"content": "hello here world", "language": "en"}]
#
#     for dictionary in file_content_dictionaries:
#         json_content[CONTENT_KEY].append(dictionary[CONTENT_KEY])
#         json_content[CONTENT_LANGUAGE].append(dictionary[CONTENT_LANGUAGE])
#     json_content[CONTENT_KEY] = " ".join(json_content[CONTENT_KEY])
#     json_content[CONTENT_LANGUAGE] = str(json_content[CONTENT_LANGUAGE][0])
#     print(json_content)

# def test_df():
#     json_content = {
#             "work": "http://publications.europa.eu/resource/cellar/1b0572d2-d1f3-11e8-9424-01aa75ed71a1",
#             "title": "COMMISSION DELEGATED REGULATION (EU) …/.. and presentation",
#             "cdm_types": "http://publications.europa.eu/ontology/cdm#work",
#
#             "core":
#                 [
#                     "true"
#                 ],
#             "eu_cellar_core": "null",
#             "eu_cellar_extended": "null",
#             "content_path":
#                 [
#                     "res/3ebbf43df528d345ba63f0556afd8fb09e4c8b4126bba4d7a7af280c2b81018a_html.zip"
#                 ]
#         }
#     df=pd.DataFrame(data=json_content, index=["3ebbf43df528d345ba63f0556afd8fb09e4c8b4126bba4d7a7af280c2b81018a"])
#     print(df)
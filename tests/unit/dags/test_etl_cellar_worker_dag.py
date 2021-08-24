import hashlib
import json
import pathlib
import re

import pandas as pd
import pytest

from sem_covid.entrypoints.etl_dags.etl_cellar_master_dag import DOCUMENTS_PREFIX, RESOURCE_FILE_PREFIX
from sem_covid.entrypoints.etl_dags.etl_cellar_worker_dag import download_manifestation_file, CellarDagWorker, \
    get_work_uri_from_context, content_cleanup_tool, select_relevant_files_from_temp_folder, \
    download_zip_objects_to_temp_folder, get_text_from_selected_files
from sem_covid.services.store_registry import store_registry
from tests.unit.dags.conftest import AttrDict
from tests.fake_storage import FakeObjectStore
from tests.fake_store_registry import FakeStoreRegistry

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


def test_get_work_uri_from_context():
    context1 = {}

    context = {"dag_run": AttrDict({
        "conf": {"work": "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"}})}
    response = get_work_uri_from_context(**context)
    assert response == "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"
    with pytest.raises(KeyError):
        # we test that the work uri is not in the context
        get_work_uri_from_context()


def test_content_cleanup_tool(fragment3_eu_cellar_covid):
    content = content_cleanup_tool(fragment3_eu_cellar_covid["content"])
    assert "\n" not in content
    assert "á" not in content
    assert "—" not in content
    assert "\u2014" not in content
    assert b"\u2014".decode("utf-8") not in content
    assert not re.match(r"\s\s", content)


def test_download_zip_objects_to_temp_folder():
    """
        store a zip in the fake object store
        pass the path to the test function
        assert that the extracted content is in the returned temp folder
    """

    path_to_zip_file = pathlib.Path(__file__).parent.parent.parent / "test_data" / "test_zip" / "test.zip"
    with open(path_to_zip_file, "rb") as file:
        zip_file = file.read(path_to_zip_file.stat().st_size)
        minio_client = store_registry.minio_object_store('fake_bucket')
        minio_client.put_object(object_name="test", content=zip_file)
        zip_extractor = download_zip_objects_to_temp_folder(["test"], minio_client)
        assert "/tmp/cellar_dag_" in str(zip_extractor)


def test_get_text_from_selected_files():
    path_list = [pathlib.Path(__file__).parent.parent.parent / "test_data" / "test_folder" / "two.html"]
    response = get_text_from_selected_files(path_list)
    assert isinstance(response, list)
    assert len(response[0].keys()) == 2
    assert response[0]["content"]


def test_select_relevant_files_from_temp_folder():
    temp_dir = pathlib.Path(__file__).parent.parent.parent / "test_data" / "test_folder"
    list_of_files_from_folder = select_relevant_files_from_temp_folder(temp_dir)

    assert list == type(list_of_files_from_folder)
    assert len(list_of_files_from_folder) == 2
    for file in list_of_files_from_folder:
        assert file.exists()


def test_cellar_dag_worker():
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
    context = {"dag_run": AttrDict({
        "conf": {"work": "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1"}})}

    worker_dag = CellarDagWorker(sparql_query=QUERY,
                                 sparql_endpoint_url=SPARQL_URL,
                                 minio_bucket_name=MINIO_BUCKET_NAME,
                                 store_registry=store_registry,
                                 index_name="test")
    worker_dag.extract(**context)

    assert len(minio_client.list_objects(object_name_prefix=RESOURCE_FILE_PREFIX)) > 0
    with pytest.raises(KeyError):
        # we test that the work uri is not in the context
        worker_dag.extract()

    worker_dag.transform_structure(**context)
    assert "content" in minio_client.get_object('documents/db9f1053db03dd74d0134ceee8f166a3c77d8079cd065b73bcaa113556655e7c.json')

    worker_dag.transform_content(**context)
    work_document = json.loads(minio_client.get_object("documents/db9f1053db03dd74d0134ceee8f166a3c77d8079cd065b73bcaa113556655e7c.json"))
    content = work_document["content"]
    assert "\n" not in content
    assert "á" not in content
    assert "—" not in content
    assert not re.match(r"\s\s", content)

    worker_dag.load(**context)
    es_adapter = store_registry.es_index_store()
    dataframe = es_adapter.get_dataframe("test")
    assert isinstance(dataframe, pd.DataFrame)

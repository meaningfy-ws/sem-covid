#!/usr/bin/python3

# test_etl_cellar_worker_dag.py
# Date:  01/07/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

from tests.unit.test_store.fake_store_registry import FakeStoreRegistryManager
from sem_covid.entrypoints.etl_dags.etl_cellar_worker_dag import download_manifestation_file


def test_download_manifestation_file():
    """
        assert that
        * the content is downloaded (not null)
        * the return is the filename in minio
        * the content is saved in minio
    """
    FAKE_SOURCE = {'content_path': []}
    FAKE_LOCATION_DETALIS = "http://publications.europa.eu/resource/cellar/d03caacf-a568-11ea-bb7a-01aa75ed71a1.0006.03"
    FAKE_FILE_NAME = 'file-name'
    FAKE_MINIO_BUCKET_NAME = 'fake-minio-bucket'

    store_registry = FakeStoreRegistryManager()
    minio_client = store_registry.minio_object_store(FAKE_MINIO_BUCKET_NAME)

    download_manifestation_file(FAKE_SOURCE, FAKE_LOCATION_DETALIS, FAKE_FILE_NAME, minio_client)

    print(FAKE_SOURCE)


def test_download_documents_and_enrich_json():
    """
        assert that:
        * metadata exists (was queried from cellar)
        * manifestation object paths exists in teh work document
        * manifestations exist in min io (objects exist in minio)
    """

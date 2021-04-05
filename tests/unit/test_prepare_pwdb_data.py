
import requests

from pandas import DataFrame

from tests.minio_connection import MinioTestFileCreation
from ml_experiments.services.pwdb_base_experiment import PWDBBaseExperiment

MINIO_ACCESS_KEY = '2zVld17bTfKk8iu0Eh9H74MywAeDV3WQ'
MINIO_SECRET_KEY = 'ddk9fixfI9qXiMaZu1p2a7BsgY2yDopm'
MINIO_URL = 'srv.meaningfy.ws:9000'
MINIO_TEST_BUCKET = 'test-ml-experiments'


def test_prepare_pwdb_data():

    minio = MinioTestFileCreation(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_TEST_BUCKET)
    test_dataset = minio.get_test_dataframe_from_minio()

    expected_data = {
        'Title': ['title_one', 'title_two'],
        'Background information': ['bi_one', 'bi_two'],
        'Content of measure': ['cm_one', 'cm_two'],
        'Category': [0, 1],
        'Subcategory': [0, 1],
        'Type of measure': [0, 1],
        'Target groups': ['tg_l_one|tg_l_two', 'tg_l_one_first|tg_l_two_second'],
        'Descriptive Data': [['titleone', 'bione', 'cmone'], ['titletwo', 'bitwo', 'cmtwo']]}

    expected_df = DataFrame(data=expected_data)

    pwdb_experiment = PWDBBaseExperiment(minio, requests)

    test_data_preparation = pwdb_experiment.prepare_pwdb_data(test_dataset)

    assert len(test_data_preparation) == len(expected_df)

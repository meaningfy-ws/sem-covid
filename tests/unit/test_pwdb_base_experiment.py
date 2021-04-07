import unittest

from pandas import DataFrame
from pandas.testing import assert_frame_equal, assert_series_equal

# from ml_experiments.config import config
# from tests.resources.minio_connection import MinioFakeConnection
from pytest import fixture
from datetime import datetime
from ml_experiments.services.pwdb_base_experiment import PWDBBaseExperiment
from airflow import DAG
# from tests.resources.reusable_test_data import create_expected_test_dataframe


# minio = MinioFakeConnection(config.MINIO_URL, config.MINIO_ACCESS_KEY,
#                             config.MINIO_SECRET_KEY, config.ML_EXPERIMENTS_BUCKET_NAME)
#
# obj = minio.get_object("covid19.json")
# print(type(obj))

# def test_len_of_expected_data_and_test_dataframe():
#     assert len(create_expected_test_dataframe()) == len(PWDB_PREPARE_FUNCTION)

# class TestPreparationPWDBData(unittest.TestCase):
#     TEST_DATAFRAME = minio.get_test_dataframe_from_minio()
#     PWDB_PREPARE_FUNCTION = PWDBBaseExperiment.prepare_pwdb_data(TEST_DATAFRAME)
#
#     # def test_len_of_expected_data_and_test_dataframe(self):
#     #     self.assertEqual(len(create_expected_test_dataframe()), len(self.PWDB_PREPARE_FUNCTION))
#
#     def test_compare_expected_data_with_test_dataframe(self):
#         assert_frame_equal(create_expected_test_dataframe(), self.PWDB_PREPARE_FUNCTION)
#
#     def test_descriptive_data_serial_equals_of_expected_and_test_dataframe(self):
#         assert_series_equal(create_expected_test_dataframe()['Descriptive Data'],
#                             self.PWDB_PREPARE_FUNCTION['Descriptive Data'])
#
#     def test_category_equals_of_expected_and_test_dataframe(self):
#         assert_series_equal(create_expected_test_dataframe()['Category'], self.PWDB_PREPARE_FUNCTION['Category'])
#
#     def test_subcategory_equals_of_expected_and_test_dataframe(self):
#         assert_series_equal(create_expected_test_dataframe()['Subcategory'], self.PWDB_PREPARE_FUNCTION['Subcategory'])
#
#     def test_type_of_measure_equals_of_expected_and_test_dataframe(self):
#         assert_series_equal(create_expected_test_dataframe()['Type of measure'],
#                             self.PWDB_PREPARE_FUNCTION['Type of measure'])
#
#     def test_target_groups_serial_equals_of_expected_and_test_dataframe(self):
#         assert_series_equal(create_expected_test_dataframe()['Target groups'],
#                             self.PWDB_PREPARE_FUNCTION['Target groups'])



def test_base_experiment_data_extraction(base_experiment):
    base_experiment.data_extraction()

def test_base_experiment_prepare_pwdb_data(transformed_pwdb_dataframe):
    resulting_df = PWDBBaseExperiment.prepare_pwdb_data(transformed_pwdb_dataframe)

    assert len(resulting_df) == 1
    assert len(resulting_df) != 2


def test_base_experiment_target_group_refactoring(transformed_pwdb_dataframe):
    assert False

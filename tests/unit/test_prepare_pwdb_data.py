
import unittest

from pandas import DataFrame
from pandas.testing import assert_frame_equal, assert_series_equal

from ml_experiments.config import config
from tests.minio_connection import MinioFakeConnection
from ml_experiments.services.pwdb_base_experiment import PWDBBaseExperiment


minio = MinioFakeConnection(config.MINIO_URL, config.MINIO_ACCESS_KEY,
                            config.MINIO_SECRET_KEY, config.MINIO_TEST_BUCKET)


class TestPreparationPWDBData(unittest.TestCase):
    EXPECTED_DATA = {
        'Title': ['title_one', 'title_two'],
        'Background information': ['bi_one', 'bi_two'],
        'Content of measure': ['cm_one', 'cm_two'],
        'Category': [0, 1],
        'Subcategory': [0, 1],
        'Type of measure': [0, 1],
        'Target groups': ['tg_one|tg_two', 'tg_one_first|tg_two_second'],
        'Descriptive Data': [['titleone', 'bione', 'cmone'], ['titletwo', 'bitwo', 'cmtwo']]}

    EXPECTED_DATAFRAME = DataFrame(data=EXPECTED_DATA)
    TEST_DATAFRAME = minio.get_test_dataframe_from_minio()
    PWDB_PREPARE_FUNCTION = PWDBBaseExperiment.prepare_pwdb_data(TEST_DATAFRAME)

    def test_len_of_expected_data_and_test_dataframe(self):
        self.assertEqual(len(self.EXPECTED_DATAFRAME), len(self.PWDB_PREPARE_FUNCTION))

    def test_compare_expected_data_with_test_dataframe(self):
        assert_frame_equal(self.EXPECTED_DATAFRAME, self.PWDB_PREPARE_FUNCTION)

    def test_descriptive_data_serial_equals_of_expected_and_test_dataframe(self):
        assert_series_equal(self.EXPECTED_DATAFRAME['Descriptive Data'], self.PWDB_PREPARE_FUNCTION['Descriptive Data'])

    def test_category_equals_of_expected_and_test_dataframe(self):
        assert_series_equal(self.EXPECTED_DATAFRAME['Category'], self.PWDB_PREPARE_FUNCTION['Category'])

    def test_subcategory_equals_of_expected_and_test_dataframe(self):
        assert_series_equal(self.EXPECTED_DATAFRAME['Subcategory'], self.PWDB_PREPARE_FUNCTION['Subcategory'])

    def test_type_of_measure_equals_of_expected_and_test_dataframe(self):
        assert_series_equal(self.EXPECTED_DATAFRAME['Type of measure'], self.PWDB_PREPARE_FUNCTION['Type of measure'])

    def test_target_groups_serial_equals_of_expected_and_test_dataframe(self):
        assert_series_equal(self.EXPECTED_DATAFRAME['Target groups'], self.PWDB_PREPARE_FUNCTION['Target groups'])

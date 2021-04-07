
from pickle import dumps, loads

import pandas as pd
from pandas import DataFrame

from ml_experiments.adapters.minio_adapter import MinioAdapter


class MinioFakeConnection(MinioAdapter):
    def get_test_dataframe_from_minio(self) -> DataFrame:
        test_dataframe = self.create_test_dataframe()
        pickle_test_dataframe = dumps(test_dataframe)
        self.put_object("test_dataframe.pkl", pickle_test_dataframe)
        test_dataframe = loads(self.get_object("test_dataframe.pkl"))

        return test_dataframe

    @staticmethod
    def create_test_dataframe() -> DataFrame:
        """
            The important step is to create testing dataframe and most important
            is to create the same column names and values types
            :return: prepared testing dataframe
        """
        data = {'Title': ['title_one', 'title_two'], 'Background information': ['bi_one', 'bi_two'],
                'Content of measure': ['cm_one', 'cm_two'], 'Category': ['cm_one', 'cm_two'],
                'Subcategory': ['sub_one', 'sub_two'], 'Type of measure': ['tom_one', 'tom_two'],
                'Target groups': [['tg_one', 'tg_two'], ['tg_one_first', 'tg_two_second']]}
        dataframe = pd.DataFrame(data=data)

        return dataframe

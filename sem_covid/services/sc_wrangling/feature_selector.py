
import pandas as pd
from pandas import DataFrame


def reduce_array_column(data_frame: DataFrame, column: str, new_column=None):
    """
        assuming that the column contains array objects,
        reduces thse arrays to a string of concatenated values
        :data_frame: the pandas DataFrame
        :column: the column with array values
        :new_column: the new column where the concatenated strings are placed;
                     If the new_column is None then the original column is replaced
    """
    if new_column:
        data_frame[new_column] = data_frame[column].apply(lambda x: "|".join(sorted(x)))
    else:
        data_frame[column] = data_frame[column].apply(lambda x: "|".join(sorted(x)))

    return data_frame


def multi_label_column_to_binary_columns(data_frame: DataFrame, column: str):
    """
        assuming that the column contains array objects,
        returns a new dataframe with binary columns (True/False)
        indicating presence of each distinct array element.

        :data_frame: the pandas DataFrame
        :column: the column with array values
        :return: a new DataFrame with binary columns
    """
    label_unique_values = data_frame[column].str.replace("'", '').str.split(',').explode().to_frame()
    drop_identical_values = label_unique_values[column].drop_duplicates(keep="first").tolist()
    multi_label_data_frame = pd.concat([data_frame,
                                        pd.crosstab(label_unique_values.index,
                                                    label_unique_values[column])[drop_identical_values]], axis=1)

    return multi_label_data_frame

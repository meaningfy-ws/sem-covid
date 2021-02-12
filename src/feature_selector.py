
import pandas as pd
from pandas import DataFrame


def reduce_array_column(df: DataFrame, column: str, new_column=None):
    """
        assuming that the column contains array objects,
        reduces thse arrays to a string of concatenated values
        :df: the pandas DataFrame
        :column: the column with array values
        :new_column: the new column where the concatenated strings are placed;
                     If the new_column is None then the original column is replaced
    """
    if new_column:
        df[new_column] = df[column].apply(lambda x: "|".join(sorted(x)))
    else:
        df[column] = df[column].apply(lambda x: "|".join(sorted(x)))

    return df


def multi_label_column_to_binary_columns(df: DataFrame, column: str):
    """
        assuming that the column contains array objects,
        returns a new dataframe with binary columns (True/False)
        indicating presence of each distinct array element.

        :df: the pandas DataFrame
        :column: the column with array values
        :return: a new DataFrame with binary columns
    """
    s = df[column].str.replace("'", '').str.split(',').explode().to_frame()
    cols = s[column].drop_duplicates(keep="first").tolist()
    df2 = pd.concat([df, pd.crosstab(s.index, s[column])[cols]], axis=1)

    return df2

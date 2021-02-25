from pandas import DataFrame


def transform_series_to_dictionary(data_frame: DataFrame, key_column: str, value_column: str):
    """
        assuming we have a table and we want to transform some Series from DataFrame into a dictionary
        :param data_frame: The DataFrame we want to use for transforming
        :param key_column: The column that will have keys for dictionary
        :param value_column: The column that will have values for dictionary
        :return: A dictionary based on selected DataFrame and his columns
    """
    dictionary = {key: value for key, value in zip(data_frame[key_column], data_frame[value_column])}

    return dictionary

from pandas import DataFrame


def series_pair_to_dict(data_frame: DataFrame, key_column: str, value_column: str):
    """
        assuming that we want to transform two Dataframe columns into a dictionary, where the first
        column acts as unique keys and the second acts as values. Note that the key uniqueness is not verified.
        If there are multiple records with the same key, then only the latest (value) is considered
        :param data_frame: The DataFrame we want to use for transforming
        :param key_column: The column that will have keys for dictionary
        :param value_column: The column that will have values for dictionary
        :return: A dictionary based on selected DataFrame and his columns
    """
    dictionary = {key: value for key, value in zip(data_frame[key_column], data_frame[value_column])}

    return dictionary

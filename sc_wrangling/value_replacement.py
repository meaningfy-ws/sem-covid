from pandas import DataFrame


def replace_values_with_numbers(data_frame: DataFrame, column: str):
    """
        assuming we have column's values in DataFrame we want to
        transform in numbers
        :data_frame: the table where the column is
        :column: the column where is the values we want to transform
        :return: the columns with replaced values
    """
    return data_frame.replace(to_replace={
        column: {
            value: number for value, number in zip(set(data_frame[column]), range(len(set(data_frame[column]))))
        }
    })


import pandas as pd


def convert_to_binary_matrix(data: pd.DataFrame) -> pd.DataFrame:
    """
     Function to get binary-matrix from DataFrame
    """
    binary_matrix = pd.DataFrame([],dtype=object)
    for index, row in data.iterrows():
        new_row = {}
        for key in row.index:
            if type(row[key]) == list:
                for column in row[key]:
                    try:
                        new_row[column] = 1
                    except Exception as e:
                        print(column, type(column))
            else:
                new_row[row[key]] = 1
        binary_matrix = binary_matrix.append(new_row, ignore_index=True)
    binary_matrix = binary_matrix.fillna(0)
    return binary_matrix


def dependency_table(data: pd.DataFrame, dependency_level: float = 0.9) -> pd.DataFrame:
    """
    Function to get dependency between columns in binary-matrix
    """
    result = {}
    for column in data.columns:
        tmp = data.loc[data[column] == 1].copy()
        tmp = tmp.sum()
        tmp /= tmp[column]
        tmp = tmp.drop(column)
        tmp = tmp.loc[tmp.values >= dependency_level]
        new_row = {}
        if tmp.size > 0:
            for index in tmp.index:
                new_row[index] = tmp[index]
            result[column] = new_row
    return pd.DataFrame(result).fillna(0)

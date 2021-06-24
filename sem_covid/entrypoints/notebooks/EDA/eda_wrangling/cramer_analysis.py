import numpy as np
import pandas as pd

from scipy.stats import chi2_contingency
from sklearn import preprocessing


def calc_cramer_v(var_1: pd.Series, var_2: pd.Series) -> float:
    """
    Function for computing Cramer's V coefficient
    """
    crosstab = np.array(pd.crosstab(var_1, var_2, rownames=None, colnames=None))
    stat = chi2_contingency(crosstab)[0]
    obs = np.sum(crosstab)
    min_ = min(crosstab.shape) - 1
    return stat / (obs * min_)


def get_cramer_corr_matrix(data: pd.DataFrame) -> pd.DataFrame:
    """
    Function for getting Cramer Correlation Matrix
    """
    le = preprocessing.LabelEncoder()
    data_encoded = pd.DataFrame()

    for col in data.columns:
        data_encoded[col] = le.fit_transform(data[col])

    rows = []

    for var_name_1 in data_encoded:
        cols = []
        for var_name_2 in data_encoded:
            cramer_v = calc_cramer_v(data_encoded[var_name_1], data_encoded[var_name_2])
            cols.append(round(cramer_v, 2))
        rows.append(cols)

    results = np.array(rows)
    cramer_corr = pd.DataFrame(results, index=data_encoded.columns, columns=data_encoded.columns)

    return cramer_corr

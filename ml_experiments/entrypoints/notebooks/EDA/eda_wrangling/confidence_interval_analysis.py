
import statsmodels.api as sm
import scipy.stats as stats

import pandas as pd
import numpy as np


def confidence_interval_with_mean(series: pd.Series):
    se = tmp_s.std() / np.sqrt(series.size)
    mean = tmp_s.mean()
    z = 1.96
    return [round(100*(mean - z*se), 2), round(100*(mean + z*se), 2)]


def confidence_interval_for_proportion(series: pd.Series):
    conf_int = [list(sm.stats.proportion_confint(n * p, n)) for p in tmp_s]
    conf_int = pd.DataFrame(conf_int).apply(lambda x: round(100*x,2))
    conf_int = [pd.Interval(row[0], row[1], closed='both') for index,row in conf_int.iterrows()]
    return conf_int


def z_score_for_series(series: pd.Series):
    return pd.Series(stats.zscore(tmp_s)).apply(lambda x: round(x, 2))

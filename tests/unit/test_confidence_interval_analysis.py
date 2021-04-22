
import pandas as pd
import numpy as np


from ml_experiments.entrypoints.notebooks.EDA.eda_wrangling.confidence_interval_analysis import (
    confidence_interval_with_mean, confidence_interval_for_proportion, z_score_for_series)

from ml_experiments.entrypoints.notebooks.EDA.eda_wrangling.binary_matrix import convert_to_binary_matrix


def test_confidence_interval_with_mean(transformed_pwdb_dataframe):
    pwdb_binary = convert_to_binary_matrix(transformed_pwdb_dataframe)
    confidence_interval_mean = confidence_interval_with_mean(pwdb_binary['Austria'])
    
    assert len(confidence_interval_mean) == 2
    assert confidence_interval_mean == [100.0, 100.0]
    assert confidence_interval_mean != [0.0, 0.0]
    

def test_confidence_interval_for_proportion(transformed_pwdb_dataframe):
    pwdb_binary = convert_to_binary_matrix(transformed_pwdb_dataframe)
    confidence_interval_proportion = confidence_interval_for_proportion(pwdb_binary['Austria'])
    
    assert type(confidence_interval_proportion) == list
    assert confidence_interval_proportion == [pd.Interval(100.0, 100.0, closed='both'), pd.Interval(100.0, 100.0, closed='both')]
    
    
def test_z_score_for_series(transformed_pwdb_dataframe):
    pwdb_binary = convert_to_binary_matrix(transformed_pwdb_dataframe)
    series_z_score = z_score_for_series(pwdb_binary['Austria'])
    
    assert type(series_z_score) == pd.core.series.Series
    assert len(series_z_score) == 2
    assert series_z_score.dtype == 'float64'
    assert type(series_z_score[0]) == np.float64
    

from IPython.display import display

import pandas as pd

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.data_observations import (plot_pie_chart, plot_bar_chart,
                                                                                 calc_freq_missing_data,
                                                                                 calc_freq_categorical_data)


def fast_categorical_analyze(data: pd.DataFrame, categorical_columns: list, data_title: str = 'Unknown'):
    results = {}
    abs_miss_obs = calc_freq_missing_data(data)
    display(abs_miss_obs)

    if abs_miss_obs.size > 0:
        plot_pie_chart(abs_miss_obs, data_title+' missing values').show()
    data = data[categorical_columns]
    for column_name in data.columns:
        data_column = data[column_name].explode()
        try:
            rel_obs = calc_freq_categorical_data(data_column, column_name, True)
            results[column_name] = rel_obs
            rel_obs = rel_obs.head(10)
            display(rel_obs)
            plot_bar_chart(rel_obs, column_name).show()
            plot_pie_chart(rel_obs, column_name).show()
        except:
            print('Observation on [', column_name, '] fault!')
            print('Check if column [', column_name, '] have compatible type!')
    return results

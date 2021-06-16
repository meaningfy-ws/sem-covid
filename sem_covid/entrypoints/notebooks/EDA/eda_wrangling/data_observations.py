
from collections import Counter
from IPython.core.display import Markdown, display

import pandas as pd
import plotly.express as px


def plot_bar_chart(observations: pd.DataFrame, chart_title: str) -> px:
    """
        Function for plot bar chart on observations
    """
    columns = observations.columns

    return px.bar(observations, x=columns[1], y=columns[0], title=chart_title)


def plot_pie_chart(observations: pd.DataFrame, chart_title: str) -> px:
    """
    Function for plot pie chart on observations
    """
    columns = observations.columns

    return px.pie(observations, values=columns[1], names=columns[0], title=chart_title)


def eda_display_result(result: pd.DataFrame, chart_title: str, bar_char: bool = True, pie_chart: bool = True):
    if result.size > 0:
        display(Markdown(chart_title))
        display(tuple(result))
        if bar_char:
            return plot_bar_chart(result, chart_title).show()
        if pie_chart:
            return plot_pie_chart(result, chart_title).show()


def calc_freq_categorical_data(data: pd.Series, title: str, relative: bool = False) -> pd.DataFrame:
    """
    Function for making observations on categorical data
    """
    observation_type_name = 'Absolute freq' if not relative else 'Relative freq'
    data = data.apply(lambda x: None if x == '' else x)
    data.dropna(inplace=True)
    observation = pd.DataFrame(Counter(data).most_common(), columns=[title, observation_type_name])
    if relative:
        observation[observation_type_name] /= observation[observation_type_name].sum() / 100
        observation[observation_type_name] = round(observation[observation_type_name], 2)

    return observation


def calc_freq_missing_data(data: pd.DataFrame, relative: bool = False) -> pd.DataFrame:
    """
    Function for making observations on missing data
    """
    observation_type_name = 'Absolute freq' if not relative else 'Relative freq'
    columns = data.columns
    tmp = pd.Series(dtype=object)
    for column in columns:
        series_tmp = data[column].explode()
        series_tmp = series_tmp.apply(lambda x: None if x == '' else x)
        tmp[column] = series_tmp.isnull().sum()
        if relative:
            tmp[column] /= series_tmp.size / 100
            tmp[column] = round(tmp[column], 2)
    observation = pd.DataFrame(tmp[tmp > 0], columns=[observation_type_name])
    observation.reset_index(inplace=True)

    return observation


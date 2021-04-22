
from IPython.core.display import display, Markdown

import pandas as pd
import plotly.express as px

from ml_experiments.entrypoints.notebooks.EDA.eda_wrangling.binary_matrix import (convert_to_binary_matrix,
                                                                                  dependency_table)


def class_collision_in_columns(data: pd.DataFrame):
    """
    Categorical data collision analysis in columns
    """
    for column in data.columns:
        series = data[column]
        tmp_df = pd.DataFrame({column: series.values})
        btable = convert_to_binary_matrix(tmp_df)
        dtable = dependency_table(btable, 0.7)
        if dtable.size>0:
            display(Markdown(f"Collision in column : {column}"))
            display(px.imshow(dtable))


def class_collision(data: pd.DataFrame):
    """
    Analysis of categorical data collisions in DataFrame
    """
    bmat = convert_to_binary_matrix(data)
    dtable = dependency_table(bmat,0.7)
    display(Markdown("Collision in dataframe"))
    display(px.imshow(dtable))
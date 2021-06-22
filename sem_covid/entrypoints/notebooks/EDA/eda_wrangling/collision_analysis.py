
from IPython.core.display import display, Markdown

import pandas as pd
import plotly.express as px

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.binary_matrix import (convert_to_binary_matrix,
                                                                             dependency_table)


def class_collision_in_columns(data: pd.DataFrame) -> display:
    """
    Categorical data collision analysis in columns
    """
    for column in data.columns:
        series = data[column]
        tmp_df = pd.DataFrame({column: series.values})
        b_table = convert_to_binary_matrix(tmp_df)
        d_table = dependency_table(b_table, 0.7)
        if d_table.size > 0:
            display(Markdown(f"Collision in column : {column}"))
            display(px.imshow(d_table))


def class_collision(data: pd.DataFrame) -> display:
    """
    Analysis of categorical data collisions in DataFrame
    """
    b_mat = convert_to_binary_matrix(data)
    d_table = dependency_table(b_mat, 0.7)
    display(Markdown("Collision in dataframe"))
    display(px.imshow(d_table))

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.collision_analysis import (
    class_collision_in_columns, class_collision)


# TODO: where is the assertion?
def test_class_collision_in_columns(transformed_pwdb_dataframe):
    class_collision_in_columns(transformed_pwdb_dataframe)


# TODO: What are we testing here?
def test_class_collision(transformed_pwdb_dataframe):
    class_collision(transformed_pwdb_dataframe)

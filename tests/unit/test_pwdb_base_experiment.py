
from datetime import datetime
from ml_experiments.services.pwdb_base_experiment import PWDBBaseExperiment
from airflow import DAG


def test_dummy_dag_creation(base_experiment):
    dummy_experiment_dag = base_experiment.create_dag(start_date=datetime.now())
    assert isinstance(dummy_experiment_dag, DAG)
    assert "Experiment" in dummy_experiment_dag.dag_id


def test_dummy_dag_anatomy(base_experiment):
    dummy_experiment_dag = base_experiment.create_dag(start_date=datetime.now())
    assert dummy_experiment_dag.default_args
    assert len(dummy_experiment_dag.task_ids) == 6
    assert 'model_training_step' in dummy_experiment_dag.task_ids
    model_training_step = dummy_experiment_dag.get_task('model_training_step')
    assert 'model_evaluation_step' in model_training_step.downstream_task_ids
    assert 'data_preparation_step' in model_training_step.upstream_task_ids


def test_kw_injection():
    def f(**kwargs):
        kwargs["x"] = kwargs.get("x", 5)
        return kwargs

    assert f(x=10)["x"] == 10
    assert f()["x"] == 5


def test_base_experiment_data_extraction(base_experiment):
    base_experiment.data_extraction()


def test_base_experiment_prepare_pwdb_data(transformed_pwdb_dataframe):
    resulting_df = PWDBBaseExperiment.prepare_pwdb_data(transformed_pwdb_dataframe)

    assert len(resulting_df) == 1
    assert len(resulting_df) != 2
    assert "Title" in resulting_df
    assert "Background information" in resulting_df
    assert "Content of measure" in resulting_df
    assert "Use of measure" in resulting_df
    assert "Views of social partners" in resulting_df
    assert "|" in resulting_df['Target groups'][0]
    assert "Descriptive Data" in resulting_df
    assert "Category" in resulting_df
    assert "Subcategory" in resulting_df
    assert "Type of measure" in resulting_df
    assert "hardship" in resulting_df["Descriptive Data"][0]
    assert "billion fund to mitigate" in resulting_df["Background information"][0]
    assert "The support is a one-off payment" in resulting_df["Content of measure"][0]
    assert "applications for phase" in resulting_df["Use of measure"][0]
    assert "Federal Economic Chamber" in resulting_df["Views of social partners"][0]
    assert "self-employedpart" not in resulting_df["Descriptive Data"][0]
    assert "schemessupport" not in resulting_df["Descriptive Data"][0]
    assert "januaryinformation" not in resulting_df["Descriptive Data"][0]
    assert "subsidiesfederal" not in resulting_df["Descriptive Data"][0]
    assert "\u20ac4" not in resulting_df["Descriptive Data"][0]
    assert "2020" not in resulting_df["Descriptive Data"][0]
    assert "\r\r" not in resulting_df["Descriptive Data"][0]
    assert "100,000" not in resulting_df["Descriptive Data"][0]
    assert "(mid-July to mid-August)" not in resulting_df["Descriptive Data"][0]
    assert "(35%)" not in resulting_df["Descriptive Data"][0]
    assert "Economic" not in resulting_df["Descriptive Data"][0]
    assert "fund:" not in resulting_df["Descriptive Data"][0]
    assert 0 in resulting_df['Category']
    assert 0 in resulting_df['Subcategory']
    assert 0 in resulting_df['Type of measure']
    assert "Income protection beyond short-time work" not in resulting_df['Category']
    assert "Extensions of  income support to workers not covered by any kind of protection scheme" \
           not in resulting_df['Subcategory']
    assert "Legislations or other statutory regulations" not in resulting_df['Type of measure']


def test_base_experiment_target_group_refactoring(transformed_pwdb_dataframe):
    prepare_pwdb_dataframe = PWDBBaseExperiment.prepare_pwdb_data(transformed_pwdb_dataframe)
    resulting_df = PWDBBaseExperiment.target_group_refactoring(prepare_pwdb_dataframe)

    assert len(resulting_df) == 1
    assert "Descriptive Data" in resulting_df
    assert "Businesses" in resulting_df
    assert "Citizens" in resulting_df
    assert "Workers" in resulting_df
    assert 1 or 0 in resulting_df['Businesses']
    assert 1 or 0 in resulting_df['Citizens']
    assert 1 or 0 in resulting_df['Workers']


# def test_train_pwdb_data(transformed_pwdb_dataframe):
#     prepare_pwdb_dataframe = PWDBBaseExperiment.prepare_pwdb_data(transformed_pwdb_dataframe)
#     pwdb_target_groups_refactor = PWDBBaseExperiment.target_group_refactoring(prepare_pwdb_dataframe)
#     resulting_df = PWDBBaseExperiment.train_pwdb_data(pwdb_target_groups_refactor)




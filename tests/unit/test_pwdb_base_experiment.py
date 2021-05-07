
from datetime import datetime
from tests.unit.conftest import FakeTabularDataSource
from sem_covid.services.pwdb_base_experiment import PWDBBaseExperiment
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

    assert len(resulting_df) == 2
    assert len(resulting_df) != 3
    assert "title" in resulting_df
    assert "background_info_description" in resulting_df
    assert "content_of_measure_description" in resulting_df
    assert "use_of_measure_description" in resulting_df
    assert "involvement_of_social_partners_description" in resulting_df
    assert "|" in resulting_df['target_groups'][0]
    assert "descriptive_data" in resulting_df
    assert "category" in resulting_df
    assert "subcategory" in resulting_df
    assert "type_of_measure" in resulting_df
    assert "hardship" in resulting_df["descriptive_data"][0]
    assert "billion fund to mitigate" in resulting_df["background_info_description"][0]
    assert "The support is a one-off payment" in resulting_df["content_of_measure_description"][0]
    assert "applications for phase" in resulting_df["use_of_measure_description"][0]
    assert "Federal Economic Chamber" in resulting_df["involvement_of_social_partners_description"][0]
    assert "self-employedpart" not in resulting_df["descriptive_data"][0]
    assert "schemessupport" not in resulting_df["descriptive_data"][0]
    assert "januaryinformation" not in resulting_df["descriptive_data"][0]
    assert "subsidiesfederal" not in resulting_df["descriptive_data"][0]
    assert "\u20ac4" not in resulting_df["descriptive_data"][0]
    assert "2020" not in resulting_df["descriptive_data"][0]
    assert "\r\r" not in resulting_df["descriptive_data"][0]
    assert "100,000" not in resulting_df["descriptive_data"][0]
    assert "(mid-July to mid-August)" not in resulting_df["descriptive_data"][0]
    assert "(35%)" not in resulting_df["descriptive_data"][0]
    assert "Economic" not in resulting_df["descriptive_data"][0]
    assert "fund:" not in resulting_df["descriptive_data"][0]
    assert 0 in resulting_df['category']
    assert 0 in resulting_df['subcategory']
    assert 0 in resulting_df['type_of_measure']
    assert "Income protection beyond short-time work" not in resulting_df['category']
    assert "Extensions of  income support to workers not covered by any kind of protection scheme" \
           not in resulting_df['subcategory']
    assert "Legislations or other statutory regulations" not in resulting_df['type_of_measure']


def test_base_experiment_target_group_refactoring(transformed_pwdb_dataframe):
    prepare_pwdb_dataframe = PWDBBaseExperiment.prepare_pwdb_data(transformed_pwdb_dataframe)
    resulting_df = PWDBBaseExperiment.target_group_refactoring(prepare_pwdb_dataframe)

    assert len(resulting_df) == 2
    assert "descriptive_data" in resulting_df
    assert "Businesses" in resulting_df
    assert "Citizens" in resulting_df
    assert "Workers" in resulting_df
    assert 1 or 0 in resulting_df['Businesses']
    assert 1 or 0 in resulting_df['Citizens']
    assert 1 or 0 in resulting_df['Workers']


def test_train_pwdb_data(transformed_pwdb_dataframe):
    prepare_pwdb_dataframe = PWDBBaseExperiment.prepare_pwdb_data(transformed_pwdb_dataframe)
    pwdb_target_groups_refactor = PWDBBaseExperiment.target_group_refactoring(prepare_pwdb_dataframe)
    resulting_df = PWDBBaseExperiment.train_pwdb_data(pwdb_target_groups_refactor)

    assert len(resulting_df) == 4
    assert "X_test" in resulting_df
    assert "X_train" in resulting_df
    assert "y_test" in resulting_df
    assert "y_train" in resulting_df
    assert "hardship" in resulting_df['X_train'][0]
    assert "category" in resulting_df["y_train"]
    assert "subcategory" in resulting_df["y_train"]
    assert "type_of_measure" in resulting_df["y_train"]
    assert "Businesses" in resulting_df["y_train"]
    assert "Workers" in resulting_df["y_train"]
    assert "Citizens" in resulting_df["y_train"]


def test_data_extraction_with_data_registry(base_experiment):
    base_experiment.data_preparation()


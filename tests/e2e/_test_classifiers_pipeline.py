import os

from sem_covid.entrypoints.ml_dags.classifiers_dag import classifiers_pipeline_dag


def test_pwdb_classifiers_feature_engineering():
    classifiers_pipeline_dag.feature_engineering()


def test_pwdb_classifiers_model_training():
    assert "AWS_SECRET_ACCESS_KEY" in os.environ.keys()
    assert "AWS_ACCESS_KEY_ID" in os.environ.keys()
    classifiers_pipeline_dag.model_training()

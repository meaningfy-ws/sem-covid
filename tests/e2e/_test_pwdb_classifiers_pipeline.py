import os

from sem_covid.services.ml_pipelines.pwdb_classifiers_pipeline import PWDBClassifiers


def test_pwdb_classifiers_feature_engineering():
    PWDBClassifiers.feature_engineering()


def test_pwdb_classifiers_model_training():
    assert "AWS_SECRET_ACCESS_KEY" in os.environ.keys()
    assert "AWS_ACCESS_KEY_ID" in os.environ.keys()
    PWDBClassifiers.model_training()


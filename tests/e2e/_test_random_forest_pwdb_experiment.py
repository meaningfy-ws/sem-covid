import os
from sem_covid.services.ml_pipelines.pwdb_random_forest_experiment import RandomForestPWDBExperiment


def test_random_forest_pwdb_feature_engineering():
    RandomForestPWDBExperiment.feature_engineering()


def test_random_forest_pwdb_model_training():
    assert "AWS_SECRET_ACCESS_KEY" in os.environ.keys()
    assert "AWS_ACCESS_KEY_ID" in os.environ.keys()
    RandomForestPWDBExperiment.model_training()

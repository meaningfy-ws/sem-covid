from sem_covid.services.pwdb_random_forest_experiment import RandomForestPWDBExperiment, FeatureEngineering


def test_random_forest_pwdb_feature_engineering():
    RandomForestPWDBExperiment.feature_engineering()


def test_random_forest_pwdb_model_training():
    RandomForestPWDBExperiment.model_training()

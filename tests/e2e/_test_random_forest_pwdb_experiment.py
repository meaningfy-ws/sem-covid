from gensim.models import KeyedVectors

from sem_covid.services.data_registry import LanguageModel
from sem_covid.services.pwdb_random_forest_experiment import RandomForestPWDBExperiment, FeatureEngineering

TMP_PWDB_FEATURE_STORE_NAME = 'tmp_fs_pwdb_tg1'


def test_random_forest_pwdb_feature_engineering():
    worker = FeatureEngineering(feature_store_name=TMP_PWDB_FEATURE_STORE_NAME)
    worker.load_language_model()


def test_random_forest_pwdb_experiment():
    RandomForestPWDBExperiment.feature_engineering()
    RandomForestPWDBExperiment.model_training()

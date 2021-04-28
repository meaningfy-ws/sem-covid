#!/usr/bin/python3

# __init__.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""

"""
import logging
import warnings

import dotenv

from sem_covid.base_config import BaseConfig

logger = logging.getLogger(__name__)


class SemCovidConfig(object):

    @property
    def MINIO_ACCESS_KEY(self) -> str:
        return BaseConfig.find_value()

    @property
    def MINIO_SECRET_KEY(self) -> str:
        return BaseConfig.find_value()

    @property
    def MINIO_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def ML_EXPERIMENTS_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def LANGUAGE_MODEL_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def EURLEX_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_TIMELINE_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def IRISH_TIMELINE_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def PWDB_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def LEGAL_INITIATIVES_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def TREATIES_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def SC_PWDB_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def PWDB_DATASET_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def PWDB_ES_TEST_DATA_DIRECTORY(self) -> str:
        return BaseConfig.find_value()

    @property
    def ES_PWDB_INDEX_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def ES_PWDB_INDEX_MAPPING_FILE(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_ACTION_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def IRISH_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def EURLEX_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def EURLEX_EXTENDED_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def LEGAL_INITIATIVES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def TREATIES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def PWDB_DATASET_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def PWDB_DATASET_PATH(self) -> str:
        return BaseConfig.find_value()

    @property
    def LAW2VEC_MODEL_PATH(self) -> str:
        return BaseConfig.find_value()

    @property
    def JRC2VEC_MODEL_PATH(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_PROTOCOL(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_HOST(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_PORT(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_USER(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_PASSWORD(self) -> str:
        return BaseConfig.find_value()

    @property
    def PWDB_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_CELLAR_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def TREATIES_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_ACTION_TIMELINE_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def IRELAND_ACTION_TIMELINE_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def APACHE_TIKA_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def SPLASH_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def EURLEX_SPARQL_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def LEGAL_INITIATIVES_SPARQL_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def LEGAL_INITIATIVES_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def TREATIES_SPARQL_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def PWDB_TRAIN_TEST(self):
        return BaseConfig.find_value()

    @property
    def PWDB_WORD2VEC_MODEL(self):
        return BaseConfig.find_value()

    @property
    def WORD2VEC_SVM_CATEGORY(self):
        return BaseConfig.find_value()

    @property
    def WORD2VEC_SVM_SUBCATEGORY(self):
        return BaseConfig.find_value()

    @property
    def WORD2VEC_SVM_TOM(self):
        return BaseConfig.find_value()

    @property
    def WORD2VEC_SVM_TG_L1(self):
        return BaseConfig.find_value()

    @property
    def LAW2VEC_SVM_CATEGORY(self):
        return BaseConfig.find_value()

    @property
    def LAW2VEC_SVM_SUBCATEGORY(self):
        return BaseConfig.find_value()

    @property
    def LAW2VEC_SVM_TOM(self):
        return BaseConfig.find_value()

    @property
    def LAW2VEC_SVM_TG_L1(self):
        return BaseConfig.find_value()

    @property
    def WORD2VEC_KNN_CATEGORY(self):
        return BaseConfig.find_value()

    @property
    def WORD2VEC_KNN_SUBCATEGORY(self):
        return BaseConfig.find_value()

    @property
    def WORD2VEC_KNN_TOM(self):
        return BaseConfig.find_value()

    @property
    def WORD2VEC_KNN_TG_L1(self):
        return BaseConfig.find_value()

    @property
    def LAW2VEC_KNN_CATEGORY(self):
        return BaseConfig.find_value()

    @property
    def LAW2VEC_KNN_SUBCATEGORY(self):
        return BaseConfig.find_value()

    @property
    def LAW2VEC_KNN_TOM(self):
        return BaseConfig.find_value()

    @property
    def LAW2VEC_KNN_TG_L1(self):
        return BaseConfig.find_value()


dotenv.load_dotenv()
config = SemCovidConfig()


# Set of config artefacts used in the Flask UI

class FlaskConfig:
    """
        Base Flask config
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = "PQqUot9QBc0EtqicZ8qP"
    PAGINATION_SIZE = 30


class ProductionConfig(FlaskConfig):
    """
        Production Flask config
    """


class DevelopmentConfig(FlaskConfig):
    """
    Development Flask config
    """
    DEBUG = True

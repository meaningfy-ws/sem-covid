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
    def SC_PWDB_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def PWDB_DATASET_URL(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def LAW2VEC_MODEL_PATH(self) -> str:
        return BaseConfig.find_value()

    @property
    def JRC2VEC_MODEL_PATH(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTIC_HOST(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTIC_PORT(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTIC_USER(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTIC_PASSWORD(self) -> str:
        return BaseConfig.find_value()

    @property
    def PWDB_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_CELLAR_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_ACTION_TIMELINE_IDX(self) -> str:
        return BaseConfig.find_value()

    @property
    def IRELAND_ACTION_TIMELINE_IDX(self) -> str:
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

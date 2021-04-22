#!/usr/bin/python3

# __init__.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""

"""

import logging
import os
import warnings

import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class MLExperimentsConfig:
    """
        Project wide configuration file.
    """

    @property
    def MINIO_ACCESS_KEY(self) -> str:
        value = os.environ.get('MINIO_ACCESS_KEY')
        logger.debug(value)
        return value

    @property
    def MINIO_SECRET_KEY(self) -> str:
        value = os.environ.get('MINIO_SECRET_KEY')
        logger.debug(value)
        return value

    @property
    def MINIO_URL(self) -> str:
        value = os.environ.get('MINIO_URL')
        logger.debug(value)
        return value

    @property
    def ML_EXPERIMENTS_BUCKET_NAME(self) -> str:
        value = os.environ.get('ML_EXPERIMENTS_BUCKET_NAME')
        logger.debug(value)
        return value

    @property
    def LANGUAGE_MODEL_BUCKET_NAME(self) -> str:
        value = os.environ.get('LANGUAGE_MODEL_BUCKET_NAME')
        logger.debug(value)
        return value

    @property
    def EURLEX_BUCKET_NAME(self) -> str:
        value = os.environ.get('EURLEX_BUCKET_NAME')
        logger.debug(value)
        return value

    @property
    def EU_TIMELINE_BUCKET_NAME(self) -> str:
        value = os.environ.get('EU_TIMELINE_BUCKET_NAME')
        logger.debug(value)
        return value

    @property
    def IRISH_TIMELINE_BUCKET_NAME(self) -> str:
        value = os.environ.get('IRISH_TIMELINE_BUCKET_NAME')
        logger.debug(value)
        return value

    @property
    def SC_PWDB_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        value = os.environ.get('SC_PWDB_JSON')
        logger.debug(value)
        return value

    @property
    def PWDB_DATASET_URL(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        value = os.environ.get('PWDB_DATASET_URL')
        logger.debug(value)
        return value

    @property
    def LAW2VEC_MODEL_PATH(self) -> str:
        value = os.environ.get('LAW2VEC_MODEL_PATH')
        logger.debug(value)
        return value

    @property
    def JRC2VEC_MODEL_PATH(self) -> str:
        value = os.environ.get('JRC2VEC_MODEL_PATH')
        logger.debug(value)
        return value

    @property
    def ELASTIC_HOST(self) -> str:
        value = os.environ.get('ELASTIC_HOST')
        logger.debug(value)
        return value

    @property
    def ELASTIC_PORT(self) -> str:
        value = os.environ.get('ELASTIC_PORT')
        logger.debug(value)
        return value

    @property
    def ELASTIC_USER(self) -> str:
        value = os.environ.get('ELASTIC_USER')
        logger.debug(value)
        return value

    @property
    def ELASTIC_PASSWORD(self) -> str:
        value = os.environ.get('ELASTIC_PASSWORD')
        logger.debug(value)
        return value

    @property
    def PWDB_IDX(self) -> str:
        value = os.environ.get('PWDB_IDX')
        logger.debug(value)
        return value

    @property
    def EU_CELLAR_IDX(self) -> str:
        value = os.environ.get('EU_CELLAR_IDX')
        logger.debug(value)
        return value

    @property
    def EU_ACTION_TIMELINE_IDX(self) -> str:
        value = os.environ.get('EU_ACTION_TIMELINE_IDX')
        logger.debug(value)
        return value

    @property
    def IRELAND_ACTION_TIMELINE_IDX(self) -> str:
        value = os.environ.get('IRELAND_ACTION_TIMELINE_IDX')
        logger.debug(value)
        return value


config = MLExperimentsConfig()

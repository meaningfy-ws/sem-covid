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

    #MinIO Service property

    @property
    def MINIO_ACCESS_KEY(self) -> str:
        return BaseConfig.find_value()

    @property
    def MINIO_SECRET_KEY(self) -> str:
        return BaseConfig.find_value()

    @property
    def MINIO_URL(self) -> str:
        return BaseConfig.find_value()
    #Other property

    @property
    def ML_EXPERIMENTS_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def LANGUAGE_MODEL_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    #EU_CELLAR property

    @property
    def EU_CELLAR_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_CELLAR_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def EU_CELLAR_SPARQL_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_CELLAR_EXTENDED_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    #EU_TIMELINE property

    @property
    def EU_TIMELINE_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def EU_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return BaseConfig.find_value()


    #IRELAND_TIMELINE property

    @property
    def IRELAND_TIMELINE_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def IRELAND_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return BaseConfig.find_value()

    #PWDB_COVID19 property

    @property
    def PWDB_COVID19_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def PWDB_DATASET_LOCAL_FILENAME(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def PWDB_DATASET_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def PWDB_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return BaseConfig.find_value()

    # TODO Property with undefined usage, ask Eugen about this ?
    @property
    def PWDB_ES_TEST_DATA_DIRECTORY(self) -> str:
        return BaseConfig.find_value()

    # TODO Property with undefined usage, ask Eugen about this ?
    @property
    def ES_PWDB_INDEX_MAPPING_FILE(self) -> str:
        return BaseConfig.find_value()

    # TODO Property with undefined usage, ask Eugen about this ?
    @property
    def PWDB_DATASET_PATH(self) -> str:
        return BaseConfig.find_value()

    #LEGAL_INITIATIVES property

    @property
    def LEGAL_INITIATIVES_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def LEGAL_INITIATIVES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def LEGAL_INITIATIVES_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return BaseConfig.find_value()

    # TODO Property with undefined usage, ask Eugen about this ?
    @property
    def LEGAL_INITIATIVES_SPARQL_URL(self) -> str:
        return BaseConfig.find_value()

    #TREATIES property
    @property
    def TREATIES_BUCKET_NAME(self) -> str:
        return BaseConfig.find_value()
    @property
    def TREATIES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return BaseConfig.find_value()

    @property
    def TREATIES_SPARQL_URL(self) -> str:
        return BaseConfig.find_value()

    @property
    def TREATIES_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return BaseConfig.find_value()

    #TIKA property
    @property
    def APACHE_TIKA_URL(self) -> str:
        return BaseConfig.find_value()

    #SPLASH property
    @property
    def SPLASH_URL(self) -> str:
        return BaseConfig.find_value()

    #Models property
    @property
    def LAW2VEC_MODEL_PATH(self) -> str:
        return BaseConfig.find_value()

    @property
    def JRC2VEC_MODEL_PATH(self) -> str:
        return BaseConfig.find_value()
    # ELASTICSEARCH property
    @property
    def ELASTICSEARCH_PROTOCOL(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_HOST_NAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_PORT(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_USERNAME(self) -> str:
        return BaseConfig.find_value()

    @property
    def ELASTICSEARCH_PASSWORD(self) -> str:
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

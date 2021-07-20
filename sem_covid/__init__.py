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

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from sem_covid.config_resolver import VaultAndEnvConfigResolver, EnvConfigResolver

from resources import crawlers

logger = logging.getLogger(__name__)

dotenv.load_dotenv(verbose=True, override=True)


class MinIOConfig:
    # MinIO Service property
    @property
    def MINIO_ACCESS_KEY(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def MINIO_SECRET_KEY(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def MINIO_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class MlExperimentsConfig:
    # Other property

    @property
    def ML_EXPERIMENTS_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def LANGUAGE_MODEL_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def MLFLOW_TRACKING_URI(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def AWS_ACCESS_KEY_ID(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def AWS_SECRET_ACCESS_KEY(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def MLFLOW_S3_ENDPOINT_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def MLFLOW_S3_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class EuCellarConfig:
    # EU_CELLAR property

    @property
    def EU_FINREG_CELLAR_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_FINREG_CELLAR_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_CELLAR_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_CELLAR_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_CELLAR_SPARQL_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_FINREG_CELLAR_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_CELLAR_EXTENDED_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()


class EuTimeLineConfig:
    # EU_TIMELINE property

    @property
    def EU_TIMELINE_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class IrelandTimelineConfig:
    # IRELAND_TIMELINE property

    @property
    def IRELAND_TIMELINE_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def IRELAND_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class PWDBConfig:
    # PWDB_COVID19 property

    @property
    def PWDB_COVID19_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def PWDB_DATASET_LOCAL_FILENAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def PWDB_DATASET_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def PWDB_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class LegalInitiativesConfig:
    # LEGAL_INITIATIVES property

    @property
    def LEGAL_INITIATIVES_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def LEGAL_INITIATIVES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def LEGAL_INITIATIVES_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class TreatiesConfig:
    # TREATIES property
    @property
    def TREATIES_BUCKET_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def TREATIES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def TREATIES_SPARQL_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def TREATIES_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class TikaConfig:
    # TIKA property
    @property
    def APACHE_TIKA_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class SplashConfig:
    # SPLASH property
    @property
    def SPLASH_URL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class ModelsConfig:
    # Models property
    @property
    def LAW2VEC_MODEL_PATH(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def JRC2VEC_MODEL_PATH(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class ElasticSearchConfig:
    # ELASTICSEARCH property
    @property
    def ELASTICSEARCH_PROTOCOL(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def ELASTICSEARCH_HOST_NAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def ELASTICSEARCH_PORT(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def ELASTICSEARCH_USERNAME(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()

    @property
    def ELASTICSEARCH_PASSWORD(self) -> str:
        return VaultAndEnvConfigResolver.config_resolve()


class VaultConfig:
    # Vault property

    @property
    def VAULT_ADDR(self) -> str:
        return EnvConfigResolver.config_resolve()

    @property
    def VAULT_TOKEN(self) -> str:
        return EnvConfigResolver.config_resolve()


class CrawlerConfig:

    # Crawler property
    @property
    def CRAWLER_EU_TIMELINE_SPOKEPERSONS(self) -> str:
        with pkg_resources.path(crawlers, 'eu_timeline_spokepersons_28_04_2021.json') as path:
            return str(path)

    @property
    def CRAWLER_EU_TIMELINE_PRESS_ASSISTANT(self) -> str:
        with pkg_resources.path(crawlers, 'eu_timeline_press_assistant_28_04_2021.json') as path:
            return str(path)


class SemCovidConfig(CrawlerConfig,
                     VaultConfig,
                     ElasticSearchConfig,
                     TikaConfig,
                     SplashConfig,
                     ModelsConfig,
                     TreatiesConfig,
                     LegalInitiativesConfig,
                     PWDBConfig,
                     IrelandTimelineConfig,
                     EuCellarConfig,
                     EuTimeLineConfig,
                     MlExperimentsConfig,
                     MinIOConfig
                     ):
    ...


config = SemCovidConfig()

# These configs need to appear also as ENV variables, therefore they are called explicit here
config.AWS_ACCESS_KEY_ID
config.MLFLOW_TRACKING_URI
config.MLFLOW_S3_BUCKET_NAME
config.MLFLOW_S3_ENDPOINT_URL
config.AWS_SECRET_ACCESS_KEY


# Set of config artefacts used in the Flask UI

class FlaskConfig:
    """
        Base Flask config
    """
    DEBUG = False
    TESTING = False
    PAGINATION_SIZE = 30

    @property
    def FLASK_SECRET_KEY(self):
        return VaultAndEnvConfigResolver.config_resolve();


class ProductionConfig(FlaskConfig):
    """
        Production Flask config
    """


class DevelopmentConfig(FlaskConfig):
    """
    Development Flask config
    """
    DEBUG = True

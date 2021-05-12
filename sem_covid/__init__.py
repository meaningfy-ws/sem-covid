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

from sem_covid.config_resolver import VaultConfigResolver, EnvConfigResolver

logger = logging.getLogger(__name__)

from resources import crawlers


class MinIOConfig(VaultConfigResolver):
    # MinIO Service property
    @property
    def MINIO_ACCESS_KEY(self) -> str:
        return self.config_resolve()

    @property
    def MINIO_SECRET_KEY(self) -> str:
        return self.config_resolve()

    @property
    def MINIO_URL(self) -> str:
        return self.config_resolve()


class MlExperimentsConfig(VaultConfigResolver):
    # Other property

    @property
    def ML_EXPERIMENTS_BUCKET_NAME(self) -> str:
        return self.config_resolve()

    @property
    def LANGUAGE_MODEL_BUCKET_NAME(self) -> str:
        return self.config_resolve()


class EuCellarConfig(VaultConfigResolver):
    # EU_CELLAR property

    @property
    def EU_CELLAR_BUCKET_NAME(self) -> str:
        return self.config_resolve()

    @property
    def EU_CELLAR_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return self.config_resolve()

    @property
    def EU_CELLAR_SPARQL_URL(self) -> str:
        return self.config_resolve()

    @property
    def EU_CELLAR_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return self.config_resolve()

    @property
    def EU_CELLAR_EXTENDED_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return self.config_resolve()


class EuTimeLineConfig(VaultConfigResolver):
    # EU_TIMELINE property

    @property
    def EU_TIMELINE_BUCKET_NAME(self) -> str:
        return self.config_resolve()

    @property
    def EU_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return self.config_resolve()

    @property
    def EU_TIMELINE_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return self.config_resolve()


class IrelandTimelineConfig(VaultConfigResolver):
    # IRELAND_TIMELINE property

    @property
    def IRELAND_TIMELINE_BUCKET_NAME(self) -> str:
        return self.config_resolve()

    @property
    def IRELAND_TIMELINE_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return self.config_resolve()

    @property
    def IRELAND_TIMELINE_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return self.config_resolve()


class PWDBConfig(VaultConfigResolver):
    # PWDB_COVID19 property

    @property
    def PWDB_COVID19_BUCKET_NAME(self) -> str:
        return self.config_resolve()

    @property
    def PWDB_DATASET_PATH(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return self.config_resolve()

    @property
    def PWDB_DATASET_URL(self) -> str:
        return self.config_resolve()

    @property
    def PWDB_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return self.config_resolve()


class LegalInitiativesConfig(VaultConfigResolver):
    # LEGAL_INITIATIVES property

    @property
    def LEGAL_INITIATIVES_BUCKET_NAME(self) -> str:
        return self.config_resolve()

    @property
    def LEGAL_INITIATIVES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return self.config_resolve()

    @property
    def LEGAL_INITIATIVES_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return self.config_resolve()


class TreatiesConfig(VaultConfigResolver):
    # TREATIES property
    @property
    def TREATIES_BUCKET_NAME(self) -> str:
        return self.config_resolve()

    @property
    def TREATIES_JSON(self) -> str:
        warnings.warn("only ElasticSearch Data shall be used", DeprecationWarning)
        return self.config_resolve()

    @property
    def TREATIES_SPARQL_URL(self) -> str:
        return self.config_resolve()

    @property
    def TREATIES_ELASTIC_SEARCH_INDEX_NAME(self) -> str:
        return self.config_resolve()


class TikaConfig(VaultConfigResolver):
    # TIKA property
    @property
    def APACHE_TIKA_URL(self) -> str:
        return self.config_resolve()


class SplashConfig(VaultConfigResolver):
    # SPLASH property
    @property
    def SPLASH_URL(self) -> str:
        return self.config_resolve()


class ModelsConfig(VaultConfigResolver):
    # Models property
    @property
    def LAW2VEC_MODEL_PATH(self) -> str:
        return self.config_resolve()

    @property
    def JRC2VEC_MODEL_PATH(self) -> str:
        return self.config_resolve()


class ElasticSearchConfig(VaultConfigResolver):
    # ELASTICSEARCH property
    @property
    def ELASTICSEARCH_PROTOCOL(self) -> str:
        return self.config_resolve()

    @property
    def ELASTICSEARCH_HOST_NAME(self) -> str:
        return self.config_resolve()

    @property
    def ELASTICSEARCH_PORT(self) -> str:
        return self.config_resolve()

    @property
    def ELASTICSEARCH_USERNAME(self) -> str:
        return self.config_resolve()

    @property
    def ELASTICSEARCH_PASSWORD(self) -> str:
        return self.config_resolve()


class VaultConfig(EnvConfigResolver):
    # Vault property

    @property
    def VAULT_ADDR(self) -> str:
        return self.config_resolve()

    @property
    def VAULT_TOKEN(self) -> str:
        return self.config_resolve()


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

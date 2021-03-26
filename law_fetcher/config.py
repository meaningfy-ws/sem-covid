#!/usr/bin/python3

# config.py
# Date:  24/11/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
Project wide configuration file.
"""
import logging
import os
from distutils.util import strtobool


class LawFetcherConfig:
    logger_name = 'law-fetcher'
    logger = logging.getLogger(logger_name)

    @property
    def LAW_FETCHER_LOGGER(self) -> str:
        value = self.logger_name
        self.logger.debug(value)
        return value

    @property
    def LAW_FETCHER_FLASK_SECRET_KEY(self) -> str:
        value = os.environ.get('LAW_FETCHER_FLASK_SECRET_KEY', 'secret key')
        self.logger.debug(value)
        return value

    @property
    def LAW_FETCHER_DEBUG(self) -> bool:
        value = strtobool(os.environ.get('LAW_FETCHER_DEBUG', 'true'))
        self.logger.debug(value)
        return value

    @property
    def PAGINATION_SIZE(self) -> int:
        value = os.environ.get('PAGINATION_SIZE', 20)
        self.logger.debug(value)
        return value

    @property
    def ELASTICSEARCH_DETAILS(self) -> dict:
        value = {
            'protocol': os.environ.get('ELASTICSEARCH_PROTOCOL', 'http'),
            'hostname': os.environ.get('ELASTICSEARCH_HOST_NAME', 'elasticsearch'),
            'port': int(os.environ.get('ELASTICSEARCH_HOST_PORT', '9200')),
            'user': os.environ.get('ELASTICSEARCH_USERNAME'),
            'password': os.environ.get('ELASTICSEARCH_PASSWORD')
        }
        self.logger.debug(value)
        return value

config = LawFetcherConfig()


class FlaskConfig:
    """
    Base Flask config
    """
    DEBUG = False
    TESTING = False


class ProductionConfig(FlaskConfig):
    """
    Production Flask config
    """


class DevelopmentConfig(FlaskConfig):
    """
    Development Flask config
    """
    DEBUG = True


class TestingConfig(FlaskConfig):
    """
    Testing Flask config
    """
    TESTING = True
    WTF_CSRF_ENABLED = False

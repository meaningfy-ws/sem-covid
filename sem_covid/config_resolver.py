#!/usr/bin/python3

# config_resolver.py
# Date:  22/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import inspect
import logging
import os
from abc import ABC

from sem_covid.services.secret_manager import get_vault_secret

logger = logging.getLogger(__name__)


class abstractstatic(staticmethod):
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True

    __isabstractmethod__ = True


class ConfigResolverABC(ABC):

    @classmethod
    def config_resolve(cls, default_value: str = None) -> str:
        config_name = inspect.stack()[1][3]
        return cls._config_resolve(config_name, default_value)

    @abstractstatic
    def _config_resolve(config_name: str, default_value: str = None):
        raise NotImplementedError


class EnvConfigResolver(ConfigResolverABC):

    def _config_resolve(config_name: str, default_value: str = None):
        value = os.environ.get(config_name, default=default_value)
        logger.info("[ENV] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
            default_value) + "')")
        return value


class VaultConfigResolver(ConfigResolverABC):

    def _config_resolve(config_name: str, default_value: str = None):
        value = get_vault_secret(config_name, default_value)
        logger.info("[VAULT] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
            default_value) + "')")
        return value


class VaultAndEnvConfigResolver(EnvConfigResolver):

    def _config_resolve(config_name: str, default_value: str = None):
        value = get_vault_secret(config_name, default_value)
        logger.info("[VAULT&ENV] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
            default_value) + "')")
        if value is not None:
            return value
        else:
            value = super()._config_resolve(config_name, default_value)
            logger.info(
                "[VAULT&ENV] Value of '" + str(config_name) + "' is " + str(value) + "(supplied default is '" + str(
                    default_value) + "')")
            return value

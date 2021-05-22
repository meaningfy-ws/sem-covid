#!/usr/bin/python3

# base_config.py
# Date:  22/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import inspect
import logging
import os
from airflow.models import Variable

from sem_covid.services.secret_manager import get_vault_secret

logger = logging.getLogger(__name__)


class BaseConfig(object):

    @staticmethod
    def find_value(default_value: str = None) -> str:
        """
            Will search for a variable identical to the caller this function.
            In teh following sources:
            - environment
            - Airflow
            - vault (kv)
        :param default_value: default value if the environment variable does not exist
        :return:
        """
        caller_function_name = inspect.stack()[1][3]
        value = os.environ.get(caller_function_name, default=default_value)
        if not value:
            try:
                value = Variable.get(caller_function_name)
            except Exception as ex:
                value = get_vault_secret(caller_function_name, default_value)
                if value is None:
                    raise ex
        logger.debug(value)
        return value

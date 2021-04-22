#!/usr/bin/python3

# base_config.py
# Date:  22/04/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import inspect
import logging
import os

logger = logging.getLogger(__name__)


class BaseConfig(object):

    @staticmethod
    def find_value(default_value: str = None) -> str:
        """
            Will search for an environment variable identical to the caller this function.
        :param default_value: default value if the environment variable does not exist
        :return:
        """
        caller_function_name = inspect.stack()[1][3]
        value = os.environ.get(caller_function_name, default=default_value)
        logger.debug(value)
        return value

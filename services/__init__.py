#!/usr/bin/python3

# __init__.py
# Date:  15/01/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com 

""" """
import logging.config
from pathlib import Path

logging.config.fileConfig(Path(__file__).parents[1] / 'logging.conf')

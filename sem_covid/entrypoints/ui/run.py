#!/usr/bin/python3

# run.py
# Date:  24/11/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
UI server through flask definitions.
"""
import logging

from law_fetcher.config import config
from sem_covid import ProductionConfig, DevelopmentConfig, FlaskConfig
from sem_covid.entrypoints.ui import app

if FlaskConfig.DEBUG:
    app.config.from_object(DevelopmentConfig())
else:
    app.config.from_object(ProductionConfig())

if __name__ == '__main__':
    app.run()
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

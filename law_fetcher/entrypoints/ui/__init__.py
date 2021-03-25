#!/usr/bin/python3

# main.py
# Date:  24/03/2021
# Author: Mihai Coslet
# Email: coslet.mihai@gmail.com

from flask import Flask

from law_fetcher.config import config

app = Flask(__name__)

app.config['SECRET_KEY'] = config.LAW_FETCHER_FLASK_SECRET_KEY

from . import views

#!/usr/bin/python3

# views.py
# Date:  24/11/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
UI pages
"""
import logging
from json import loads

from flask import render_template, request

from law_fetcher.config import config
from law_fetcher.entrypoints.ui import app
from law_fetcher.entrypoints.ui.forms import SearchForm

logger = logging.getLogger(config.LAW_FETCHER_LOGGER)

DEFAULT_CHOICE = ('', 'All')


def get_error_message_from_response(response):
    return f'Status: {loads(response).get("status")}. Title: {loads(response).get("title")}' \
           f' Detail: {loads(response).get("detail")}'


@app.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)

    form = SearchForm()
    form.topic.choices = [DEFAULT_CHOICE, ('law', 'Law'), ('medicine', 'Medicine')]
    form.stage.choices = [DEFAULT_CHOICE, ('stage1', 'Stage 1'), ('stage2', 'Stage 2')]
    form.act_type.choices = [DEFAULT_CHOICE, ('act1', 'Act 1'), ('act2', 'Act 2')]

    if form.validate_on_submit():
        print(form.topic.data)
        print(form.stage.data)
        print(form.act_type.data)
    logger.debug('request index view')
    return render_template('index.html', title='Law Fetcher index page', form=form)

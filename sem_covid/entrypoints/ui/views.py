#!/usr/bin/python3

# views.py
# Date:  24/11/2020
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com

"""
UI pages
"""
import logging
from math import ceil

from flask import render_template, request

from sem_covid import FlaskConfig
from sem_covid.entrypoints.ui import app
from sem_covid.entrypoints.ui.forms import SearchForm
from sem_covid.services.store_registry import StoreRegistry

logger = logging.getLogger(__name__)

DEFAULT_CHOICE = [('', 'All')]


@app.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    keywords = request.args.get('keywords', None)
    topic = request.args.get('topic', None)
    document_category = request.args.get('document_category', None)

    es_adapter = StoreRegistry.es_index_store()
    form = SearchForm()

    query = {
        "aggs": {
            "eurovoc_concept_labels": {
                "terms": {"field": "eurovoc_concept_labels.keyword"}
            }
        },
        "size": 0
    }
    concepts = es_adapter.get_aggregation(index_name='legal-initiatives-index', body=query)
    concept_choices = es_adapter.extract_aggregation_tuples(concepts, 'eurovoc_concept_labels')
    form.topic.choices = DEFAULT_CHOICE + concept_choices

    query = {
        "aggs": {
            "resource_type_labels": {
                "terms": {"field": "resource_type_labels.keyword", "size": 1000}
            }
        },
        "size": 0
    }

    resource_types = es_adapter.get_aggregation(index_name='legal-initiatives-index', body=query)
    resource_choices = es_adapter.extract_aggregation_tuples(resource_types, 'resource_type_labels')
    form.document_category.choices = DEFAULT_CHOICE + resource_choices

    if not (form.validate_on_submit()) and (keywords or topic or document_category):
        form.keywords.data = keywords
        form.topic.data = topic
        form.document_category.data = document_category

    query_match = [('title', form.keywords.data), ('content', form.keywords.data)]
    query_filter = [('eurovoc_concept_labels.keyword', form.topic.data),
                    ('resource_type_labels.keyword', form.document_category.data)]
    fields = ['title', 'eurovoc_concept_labels', 'resource_type_labels']

    if form.validate_on_submit():
        body = es_adapter.build_query(query_match, query_filter, fields)
        result = es_adapter._es.search(index='legal-initiatives-index', body=body)
        result_count = result['hits']['total']['value']
        pages = ceil(result_count / FlaskConfig.PAGINATION_SIZE)
        return render_template('index.html', title='Law Fetcher index page', form=form, data=result['hits']['hits'],
                               count=result_count, current_page=1, pages=pages)

    body = es_adapter.build_query(query_match, query_filter, fields, (page - 1) * FlaskConfig.PAGINATION_SIZE)
    result = es_adapter._es.search(index='legal-initiatives-index', body=body)
    result_count = result['hits']['total']['value']
    pages = ceil(result_count / FlaskConfig.PAGINATION_SIZE)
    return render_template('index.html', title='Law Fetcher index page', form=form, data=result['hits']['hits'],
                           count=result_count, current_page=page, pages=pages)


@app.route('/legal-initiatives/<id>', methods=['GET'])
def legal_initiatives_detail(id):
    es_adapter = StoreRegistry.es_index_store()
    document = es_adapter.get_document('legal-initiatives-index', id)

    return render_template('legal_initiatives/detail.html', title='Legal Initiatives Document',
                           document=document['_source'])

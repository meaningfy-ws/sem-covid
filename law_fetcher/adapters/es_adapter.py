#!/usr/bin/python3

# esingestadapter.py
# Date:  20/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
#
# THIS CODE IS PRE-ALPHA !
# To read:
# https://www.elastic.co/guide/en/elasticsearch/reference/current/removal-of-types.html

import base64
from typing import List

from elasticsearch import Elasticsearch

from law_fetcher.config import config


class ESAdapter:
    def __init__(self, protocol: str, hostname: str, port: int, user: str, password: str):
        self._es = Elasticsearch([protocol + '://' + user + ':' + password + '@' + hostname + ':' + str(port)])

    def get_health(self):
        return self._es.cat.health()

    def create_index(self, index_name: str):
        # ignore 400 because it means that the index already exist
        return self._es.indices.create(index=index_name, ignore=400)

    def get_index(self, index_name: str):
        return self._es.indices.get_alias(index=index_name)

    def create_pipeline(self, index_name: str, pipeline_id: str,
                        pipeline_description: str = "Extract attachment information"):
        body = {
            "description": pipeline_description,
            "processors": [
                {
                    "attachment": {
                        "field": "data"
                    }
                }
            ]
        }
        return self._es.index(index=index_name, id=pipeline_id, body=body)

    def get_pipeline(self, pipeline_id: str):
        return self._es.ingest.get_pipeline(id=pipeline_id)

    def ingest_document(self, index_name: str, payload):
        result = self._es.index(index=index_name,
                                body={'data': str(base64.b64encode(payload))})
        return result

    def get_document_by_id(self, index_name, document_id, exclude_binary_source: bool = True):
        if exclude_binary_source:
            result = self._es.get(index=index_name, id=document_id)
        else:
            result = self._es.get(index=index_name, id=document_id, _source_excludes=["data"])

        return result

    def search(self, index_name: str, query: str, exclude_binary_source: bool = True):
        if exclude_binary_source:
            result = self._es.search(index=index_name, q=query)
        else:
            result = self._es.search(index=index_name, q=query, _source_excludes=["data"])

        return result

    def get_document(self, index_name: str, id: str):
        return self._es.get(index=index_name, id=id)

    def get_aggregation(self, index_name: str, body: dict) -> dict:
        result = self._es.search(index=index_name, body=body)
        return result

    @staticmethod
    def extract_aggregation_tuples(aggregation: dict, aggregation_label: str) -> List[tuple]:
        return [(concept['key'], concept['key']) for concept in
                aggregation['aggregations'][aggregation_label]['buckets']]

    @staticmethod
    def build_query(query_match: List[tuple] = None, query_filter: List[tuple] = None, fields: list = None,
                    offset=0):

        """

        :param query_match:
        :param query_filter:
        :param fields:
        :return:
        """
        query = {
            'query': {
                'bool': {
                    'should': [],
                    'filter': []
                }
            },
            "from": offset,
            "size": config.PAGINATION_SIZE
        }
        if query_match:
            for elastic_field, value in query_match:
                if value:
                    query['query']['bool']['should'].append({'match': {elastic_field: value}})
            if query['query']['bool']['should']:
                query['query']['bool']['minimum_should_match'] = 1

        if query_filter:
            for elastic_field, value in query_filter:
                if value:
                    query['query']['bool']['filter'].append({'term': {elastic_field: value}})

        if fields:
            query['fields'] = fields
            query['_source'] = False

        return query

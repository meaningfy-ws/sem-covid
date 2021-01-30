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
from elasticsearch import Elasticsearch


class ESAdapter:
    def __init__(self, protocol: str, hostname: str, port: int, user: str, password: str):
        self.__es__ = Elasticsearch([protocol + '://' + user + ':' + password + '@' + hostname + ':' + str(port)])

    def get_health(self):
        return self.__es__.cat.health()

    def create_index(self, index_name: str):
        # ignore 400 because it means that the index already exist
        return self.__es__.indices.create(index=index_name, ignore=400)

    def get_index(self, index_name: str):
        return self.__es__.indices.get_alias(index=index_name)

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
        return self.__es__.index(index=index_name, id=pipeline_id, body=body)

    def get_pipeline(self, pipeline_id: str):
        return self.__es__.ingest.get_pipeline(id=pipeline_id)

    def ingest_document(self, index_name: str, pipeline_id: str, payload):
        result = self.__es__.index(index=index_name,
                                   # pipeline=pipeline_id,
                                   body={'data': str(base64.b64encode(payload))})
        return result

    def get_document_by_id(self, index_name, document_id, exclude_binary_source: bool = True):
        if exclude_binary_source:
            result = self.__es__.get(index=index_name, id=document_id)
        else:
            result = self.__es__.get(index=index_name, id=document_id, _source_excludes=["data"])

        return result

    def search(self, index_name: str, query: str, exclude_binary_source: bool = True):
        if exclude_binary_source:
            result = self.__es__.search(index=index_name, q=query)
        else:
            result = self.__es__.search(index=index_name, q=query, _source_excludes=["data"])

        return result

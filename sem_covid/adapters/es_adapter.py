#!/usr/bin/python3

# esingestadapter.py
# Date:  20/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
#
# THIS CODE IS PRE-ALPHA !
# To read:
# https://www.elastic.co/guide/en/elasticsearch/reference/current/removal-of-types.html

import warnings
from typing import List, Union

import pandas as pd
from es_pandas import es_pandas


# Needs:
# - dump an index, as JSON, so that it can be ingested afterwards exactly as is
#   stripped, if necessary of internal ES fields e.g. field_name.keywords,
# - dump (a) in memory, (b) to local folder or (c) to a s3 bucket

class ESAdapter:
    def __init__(self, host_name: str, port: str, user: str, password: str):

        self._es_pandas = es_pandas(hosts=[host_name],
                                    http_auth=(user, password),
                                    port=port, http_compress=True)
        self._es = self._es_pandas.es

    def index(self, index_name, document_id, document_body):
        self._es.index(index=index_name, id=document_id, body=document_body)

    def get_document(self, index_name: str, id: str):
        return self._es.get(index=index_name, id=id)

    def search(self, index_name: str, query: str, exclude_binary_source: bool = True):
        if exclude_binary_source:
            result = self._es.search(index=index_name, q=query)
        else:
            result = self._es.search(index=index_name, q=query, _source_excludes=["data"])
        return result

    def to_dataframe(self, **kwargs) -> pd.DataFrame:
        """
            scroll datas from es, and convert to dataframe, the index of dataframe is from es index,
            about 2 million records/min
        :param index: full name of es indices
        :param query_rule: the query to Elasticsearch
        :param chunk_size: maximum 10000
        :param heads: certain columns get from es fields, [] for all fields
        :param dtype: dict like, pandas dtypes for certain columns
        :param infer_dtype: bool, default False, if true, get dtype from es template
        :param show_progress: bool, default True, if true, show progressbar on console
        :param kwargs:
        :return: DataFrame
        """
        return self._es_pandas.to_pandas(**kwargs)

    def dump(self, index_name, file_path: str = None):
        """
            TODO: reuse any of these methods
                1. https://gist.github.com/spikeekips/6018427
                2. https://github.com/neilz/es_dump/blob/master/es_dump.py
                3. use bulk and scan methods described here: https://elasticsearch-py.readthedocs.io/en/master/helpers.html#bulk-helpers
        :param index_name:
        :return:
        """
        warnings.warn("Needs implementation", FutureWarning)
        # for i in elasticsearch.helpers.scan(self._es, query={"query": {"match_all": {}}}):
        #     print(i)
        # return self._es.search(index=index_name, q="*", _source_excludes=["data"], size=-1)

    # TODO: how is this aggregation compared to the search above?
    def get_aggregation(self, index_name: str, body: dict) -> dict:
        result = self._es.search(index=index_name, body=body)
        return result

    # TODO: looks lieke an util method
    @staticmethod
    def extract_aggregation_tuples(aggregation: dict, aggregation_label: str) -> List[tuple]:
        return [(concept['key'], concept['key']) for concept in
                aggregation['aggregations'][aggregation_label]['buckets']]

    @staticmethod
    def resultset_to_dataframe(query_result_set: dict) -> pd.DataFrame:
        """
            turns a resultset into a Pandas dataframe
        :param query_result_set:
        :return:
        """
        index_ids, docs = [], []
        if query_result_set['hits']:
            index_ids, docs = [hit['_id'] for hit in query_result_set['hits']['hits']], \
                              [hit['_source'] for hit in query_result_set['hits']['hits']]
        return pd.DataFrame.from_records(data=docs, index=index_ids)

    @staticmethod
    def resultset_to_json(query_result_set: dict, file_path: str = None, include_index=False) -> Union[None, str]:
        """
            Turns a result set into JSON and saves it into a file if file_path provided or returns it as a string
            TODO: add s3 storage options
            e.g. https://stackoverflow.com/questions/61253928/writing-pandas-dataframe-to-s3
            e.g. https://stackoverflow.com/questions/65711028/how-to-write-a-pandas-dataframe-to-json-to-s3-in-json-format

        :param query_result_set:
        :param file_path: File path or object. If not specified, the result is returned as a string.
        :param include_index:
        :return:
        """
        df = ESAdapter.resultset_to_dataframe(query_result_set)
        if include_index:
            df["_index"] = df.index
        return df.to_json(path_or_buf=file_path, orient='records', indent=4)

    # TODO: looks like an util method
    @staticmethod
    def build_query(query_match: List[tuple] = None, query_filter: List[tuple] = None, fields: list = None,
                    offset=0, limit=30):

        """

        :param limit: the number of returned results
        :param offset: the search result offset
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
            "size": limit
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

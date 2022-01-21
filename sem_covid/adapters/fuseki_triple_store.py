#!/usr/bin/python3

# fuseki_triple_store.py
# Date:  27/12/2021
# Author: Stratulat Ștefan

import json
from io import StringIO
from typing import List
from urllib.parse import urljoin

import pandas as pd
import rdflib
import requests
from rdflib import Graph, URIRef
from rdflib.plugins.stores import sparqlstore
from requests.auth import HTTPBasicAuth

from sem_covid.adapters.abstract_store import TripleStoreABC

DEFAULT_GRAPH_ID = "http://www.example.com/default"

class FusekiTripleStore(TripleStoreABC):
    """
        This class is an adapter for the fuseki triple store.
    """

    def __init__(self, fuseki_url: str, user_name: str, password: str):
        """
            Initializing the adapter parameters.
        :param fuseki_url: url către un fuseki triple store
        :param user_name: username
        :param password: user password
        """
        self.fuseki_url = fuseki_url
        self.user_name = user_name
        self.password = password
        self.http_client = requests

    def _get_fuseki_client(self, dataset_id: str, return_format: str = 'csv'):
        """
            This method creates a fuseki client for reading and writing to a dataset.
        :param dataset_id: The dataset identifier. This should be short alphanumeric string uniquely
        identifying the dataset
        :return:
        """
        query_endpoint = f'{self.fuseki_url}{dataset_id}/query'
        update_endpoint = f'{self.fuseki_url}{dataset_id}/update'
        store = sparqlstore.SPARQLUpdateStore(auth=(self.user_name, self.password), returnFormat=return_format)
        store.open((query_endpoint, update_endpoint))
        return store

    def create_dataset(self, dataset_id: str) -> requests.Response:
        """
            Create the dataset for the Fuseki store
        :param dataset_id: The dataset identifier. This should be short alphanumeric string uniquely
        identifying the dataset
        :return: HTTP response
        """

        data = {
            'dbType': 'tdb2',  # assuming that all databases are created persistent across restart
            'dbName': dataset_id
        }

        response = self.http_client.post(urljoin(self.fuseki_url, f"/$/datasets"),
                                         auth=HTTPBasicAuth(self.user_name,
                                                            self.password),
                                         data=data)
        return response

    def delete_dataset(self, dataset_id: str) -> requests.Response:
        """
            Delete the dataset from the Fuseki store
        :param dataset_id: The dataset identifier. This should be short alphanumeric string uniquely
        identifying the dataset
        :return: HTTP response
        """
        response = self.http_client.delete(urljoin(self.fuseki_url, f"/$/datasets/{dataset_id}"),
                                           auth=HTTPBasicAuth(self.user_name,
                                                              self.password))
        return response

    def list_datasets(self) -> List[str]:
        """
            Get the list of the dataset names from the Fuseki store.
        :return: the list of the dataset names
        :rtype: list
        """
        response = self.http_client.get(urljoin(self.fuseki_url, "/$/datasets"),
                                        auth=HTTPBasicAuth(self.user_name,
                                                           self.password))
        if response.status_code != 200:
            return []
        result = json.loads(response.text)
        return [d_item['ds.name'] for d_item in result['datasets']]

    def sparql_query(self, dataset_id: str, query: str) -> pd.DataFrame:
        """
            This method performs a SPARQL query on a specific dataset.
        :param dataset_id: The dataset identifier. This should be short alphanumeric string uniquely
        identifying the dataset
        :param query: SPARQL query
        :return: the results of the SPARQL query will be returned as a pd.DataFrame.
        """
        store = self._get_fuseki_client(dataset_id=dataset_id)
        result = store.query(query=query)
        return pd.read_csv(filepath_or_buffer=StringIO(result.serialize(format='csv').decode('utf-8')), sep=',')

    def sparql_update_query(self, dataset_id: str, query: str):
        """
            This method performs a SPARQL update query on a specific dataset.
        :param dataset_id: The dataset identifier. This should be short alphanumeric string uniquely
        identifying the dataset
        :param query: SPARQL query
        :return:
        """
        store = self._get_fuseki_client(dataset_id=dataset_id)
        store.query(query=query)

    def upload_graph(self, dataset_id: str, graph: rdflib.Graph, use_context: bool = True):
        """
           This method loads a graph into the fuseki triple store.
        :param dataset_id: The dataset identifier. This should be short alphanumeric string uniquely
        identifying the dataset
        :param graph:
        :param use_context:
        :return:
        """
        store = self._get_fuseki_client(dataset_id=dataset_id)
        store.add_graph(graph=graph)
        context = graph if use_context else None
        if context:
            store.add_graph(graph=graph)
        for spo in graph.triples(triple=(None, None, None)):
            store.add(spo=spo, context=context)
        store.commit()

    def upload_triples(self, dataset_id: str, quoted_triples: str, rdf_fmt: str, graph_id: str = None):
        """
            This method loads triplets into the fuseki triple store.
        :param dataset_id: The dataset identifier. This should be short alphanumeric string uniquely
        identifying the dataset
        :param quoted_triples: triples in textual format.
        :param rdf_fmt: rdf format (ex: turtle, ttl or turtle2, xml or pretty-xml, json-ld, ntriples, nt or nt11, n3, trig, trix )
        :param graph_id: The graph identifier.
        :return:
        """
        use_context = True if graph_id else False
        graph_id = graph_id if graph_id else DEFAULT_GRAPH_ID
        graph = Graph(identifier=URIRef(graph_id))
        graph.parse(data=quoted_triples, format=rdf_fmt)
        self.upload_graph(dataset_id=dataset_id, graph=graph, use_context=use_context)

import io
from pathlib import Path
from typing import Optional

from SPARQLWrapper import SPARQLWrapper, CSV
from py_singleton import singleton

import pandas as pd

from string import Template
from sem_covid.adapters.abstract_store import TripleStoreABC

DEFAULT_ENCODING = 'utf-8'


class SubstitutionTemplate(Template):
    delimiter = '~'


@singleton
class SPARQLClientPool(object):
    """
        A singleton connection pool, that hosts a dictionary of endpoint_urls and
        a corresponding SPARQLWrapper object connecting to it.
        The rationale of this connection pool is to reuse connection objects and save time.
    """
    connection_pool = {}

    @staticmethod
    def create_or_reuse_connection(endpoint_url: str):
        if endpoint_url not in SPARQLClientPool.connection_pool:
            SPARQLClientPool.connection_pool[endpoint_url] = SPARQLWrapper(endpoint_url)
        return SPARQLClientPool.connection_pool[endpoint_url]


# safe instantiation
SPARQLClientPool.instance()


class SPARQLTripleStore(TripleStoreABC):

    def __init__(self, endpoint_url: str):
        self.endpoint = SPARQLClientPool.create_or_reuse_connection(endpoint_url)

    def with_query(self, sparql_query: str, substitution_variables: dict = None,
                   sparql_prefixes: str = "") -> TripleStoreABC:
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """
        if substitution_variables:
            template_query = SubstitutionTemplate(sparql_query)
            sparql_query = template_query.safe_substitute(substitution_variables)

        new_query = (sparql_prefixes + " " + sparql_query).strip()

        self.endpoint.setQuery(new_query)
        return self

    def with_query_from_file(self, sparql_query_file_path: str, substitution_variables: dict = None,
                             prefixes: str = "") -> TripleStoreABC:
        """
            Set the query text and return the reference to self for chaining.
        :return:
        """

        with open(Path(sparql_query_file_path).resolve(), 'r') as file:
            query_from_file = file.read()

        if substitution_variables:
            template_query = SubstitutionTemplate(query_from_file)
            query_from_file = template_query.safe_substitute(substitution_variables)

        new_query = (prefixes + " " + query_from_file).strip()

        self.endpoint.setQuery(new_query)
        return self

    def get_dataframe(self) -> pd.DataFrame:
        if not self.endpoint.queryString or self.endpoint.queryString.isspace():
            raise Exception("The query is empty.")

        self.endpoint.setReturnFormat(CSV)
        query_result = self.endpoint.queryAndConvert()
        return pd.read_csv(io.StringIO(str(query_result, encoding=DEFAULT_ENCODING)))


    def __str__(self):
        return f"from <...{str(self.endpoint.endpoint)[-30:]}> {str(self.endpoint.queryString)[:60]} ..."

from sem_covid import config
from rdflib import Graph, Literal, URIRef
from rdflib.plugins.stores import sparqlstore
from sem_covid.adapters.minio_object_store import MinioObjectStore
from minio import Minio

query_endpoint = 'http://localhost:8595/test/query'
update_endpoint = 'http://localhost:8595/test/update'
RDF_DATA_BUCKET = 'rdf-transformer'
store = sparqlstore.SPARQLUpdateStore(auth=('admin','1234'))
store.open((query_endpoint, update_endpoint))

g = Graph(identifier = URIRef('http://www.example.com/sc-data1'))

minio_client = Minio(config.MINIO_URL,
                             access_key=config.MINIO_ACCESS_KEY,
                             secret_key=config.MINIO_SECRET_KEY,
                             secure=False)

minio_client = MinioObjectStore(minio_bucket=RDF_DATA_BUCKET,minio_client= minio_client)
raw_data = minio_client.get_object(object_name='/results/test_result.ttl').decode('utf-8')
print(raw_data)
g.parse(data=raw_data, format='nt11')
print(list(g.triples(triple=(None,None,None))))
print(g.all_nodes())
#store.add_graph(g)
for spo in g.triples(triple=(None,None,None)):
    store.add(spo=spo)
store.commit()

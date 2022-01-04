#!/usr/bin/python3

# rml_transform_pipeline.py
# Date:  30.12.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from sem_covid.adapters.rml_mapper import RMLMapperABC
from typing import List
from sem_covid.adapters.abstract_store import ObjectStoreABC, IndexStoreABC, TripleStoreABC
import numpy as np

MINIO_RML_RULES_DIR = 'rml_rules'
MINIO_RML_SOURCES_DIR = 'fields'
MINIO_RML_RESULTS_DIR = 'results'
DATASET_INDEX_NAME = 'ds_unified_dataset'
DATASET_PART_SIZE = 100
RDF_RESULT_FORMAT = 'nt11'



class RMLTransformPipeline:
    """

    """
    def __init__(self,
                 rml_rules_file_name: str,
                 source_file_names: List[str],
                 rdf_result_file_name: str,
                 rml_mapper: RMLMapperABC,
                 object_storage: ObjectStoreABC,
                 index_storage: IndexStoreABC,
                 triple_storage: TripleStoreABC,
                 use_sample_data: bool = False
                 ):
        """

        :param rml_rules_file_name:
        :param source_file_names:
        :param rdf_result_file_name:
        :param rml_mapper:
        :param object_storage:
        :param index_storage:
        :param triple_storage:
        """
        self.rml_rules_file_name = rml_rules_file_name
        self.source_file_names = source_file_names
        self.rdf_result_file_name = rdf_result_file_name
        self.rml_mapper = rml_mapper
        self.object_storage = object_storage
        self.index_storage = index_storage
        self.triple_storage = triple_storage
        self.rml_rule = None
        self.sources = None
        self.rdf_results = None
        self.dataset_parts = None
        self.use_sample_data = use_sample_data

    def extract(self):
        """

        :return:
        """
        self.rml_rule = self.object_storage.get_object(
            object_name=f'{MINIO_RML_RULES_DIR}/{self.rml_rules_file_name}').decode('utf8')
        self.sources = {
            file_name: self.object_storage.get_object(object_name=f'{MINIO_RML_SOURCES_DIR}/{file_name}').decode('utf8')
            for file_name in self.source_file_names}
        dataset = self.index_storage.get_dataframe(index_name=DATASET_INDEX_NAME)
        dataset['index'] = dataset.index
        if self.use_sample_data:
            self.dataset = dataset.head(100)
        else:
            self.dataset = dataset
        df_size = len(self.dataset)
        part_size = DATASET_PART_SIZE
        number_of_parts = int(round(df_size / part_size, 0)) + 1
        self.dataset_parts = np.array_split(self.dataset, number_of_parts)

    def transform(self):
        """

        :return:
        """
        assert self.rml_rule is not None
        assert self.sources is not None
        assert self.dataset_parts is not None
        self.rdf_results = []
        for dataset_part in self.dataset_parts:
            sources = self.sources.copy()
            sources['data.json'] = dataset_part.to_json(orient='index')
            self.rdf_results.append(self.rml_mapper.transform(rml_rule=self.rml_rule, sources=sources))
        self.rdf_results = '\n'.join(self.rdf_results)  # this is the source of potential resource issues

    def load(self):
        """

        :return:
        """
        assert self.rdf_results is not None
        self.object_storage.put_object(object_name=f'{MINIO_RML_RESULTS_DIR}/{self.rdf_result_file_name}',
                                       content=self.rdf_results.encode('utf8'))
        self.triple_storage.create_dataset(dataset_id=DATASET_INDEX_NAME)
        self.triple_storage.upload_triples(dataset_id=DATASET_INDEX_NAME, quoted_triples=self.rdf_results,
                                           rdf_fmt=RDF_RESULT_FORMAT)

    def execute(self):
        """

        :return:
        """
        self.extract()
        self.transform()
        self.load()
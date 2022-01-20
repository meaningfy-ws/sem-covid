import json
import numpy as np
from sem_covid.adapters.abstract_store import ObjectStoreABC, FeatureStoreABC, TripleStoreABC
from sem_covid.adapters.rml_mapper import RMLMapperABC

MINIO_RML_RULES_DIR = 'rml_rules'
MINIO_RML_RESULTS_DIR = 'results'
DATASET_INDEX_NAME = 'ds_unified_similarity_matrix'
DATASET_PART_SIZE = 100
RDF_RESULT_FORMAT = 'nt11'

class SemanticSimilarityMapRMLTransformPipeline:
    """

    """
    def __init__(self,
                 rml_rules_file_name: str,
                 source_file_name: str,
                 rdf_result_file_name: str,
                 rml_mapper: RMLMapperABC,
                 object_storage: ObjectStoreABC,
                 feature_storage: FeatureStoreABC,
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
        self.source_file_name = source_file_name
        self.rdf_result_file_name = rdf_result_file_name
        self.rml_mapper = rml_mapper
        self.object_storage = object_storage
        self.feature_storage = feature_storage
        self.triple_storage = triple_storage
        self.rml_rule = None
        self.dataset = None
        self.rdf_results = None
        self.dataset_parts = None
        self.use_sample_data = use_sample_data

    def extract(self):
        """

        :return:
        """
        self.rml_rule = self.object_storage.get_object(
            object_name=f'{MINIO_RML_RULES_DIR}/{self.rml_rules_file_name}').decode('utf8')
        dataset = self.feature_storage.get_features(features_name=self.source_file_name)
        if self.use_sample_data:
            self.dataset = dataset.head(100)
        else:
            self.dataset = dataset
        number_of_parts = len(self.dataset)//DATASET_PART_SIZE + 1
        self.dataset_parts = np.array_split(self.dataset, number_of_parts)

    def transform(self):
        """

        :return:
        """
        assert self.rml_rule is not None
        assert self.dataset_parts is not None
        self.rdf_results = []
        for dataset_part in self.dataset_parts:
            result = []
            for iter, rows in dataset_part.iterrows():
                result+=[{"measure_src": iter,"measure_dest": dest, "similarity": rows[dest]} for dest in rows.index]
            json_result = json.dumps({'similarity_matrix':result})
            sources = {'ds_unified_sem_similarity_matrix.json': json_result}
            self.rdf_results.append(self.rml_mapper.transform(rml_rule=self.rml_rule, sources=sources))

    def load(self):
        """

        :return:
        """
        assert self.rdf_results is not None
        self.triple_storage.create_dataset(dataset_id=DATASET_INDEX_NAME)
        for rdf_result  in self.rdf_results:
            self.triple_storage.upload_triples(dataset_id=DATASET_INDEX_NAME, quoted_triples=rdf_result,
                                               rdf_fmt=RDF_RESULT_FORMAT)
        rdf_full_result = '\n'.join(self.rdf_results)
        self.object_storage.put_object(object_name=f'{MINIO_RML_RESULTS_DIR}/{self.rdf_result_file_name}',
                                       content=rdf_full_result.encode('utf8'))

    def execute(self):
        """

        :return:
        """
        self.extract()
        self.transform()
        self.load()
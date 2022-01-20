from sem_covid.adapters.abstract_store import ObjectStoreABC, TripleStoreABC
from sem_covid.adapters.rml_mapper import RMLMapperABC

MINIO_RML_RULES_DIR = 'rml_rules'
MINIO_RML_RESULTS_DIR = 'results'
MINIO_RML_FIELDS_DIR = 'fields'
DATASET_INDEX_NAME = 'ds_unified_topics'
RDF_RESULT_FORMAT = 'nt11'


class TopicsTransformPipeline:
    """

    """

    def __init__(self,
                 rml_rules_file_name: str,
                 source_file_name: str,
                 rdf_result_file_name: str,
                 rml_mapper: RMLMapperABC,
                 object_storage: ObjectStoreABC,
                 triple_storage: TripleStoreABC,
                 ):
        """
        
        :param rml_rules_file_name:
        :param source_file_name:
        :param rdf_result_file_name:
        :param rml_mapper:
        :param object_storage:
        :param triple_storage:
        """
        self.rml_rules_file_name = rml_rules_file_name
        self.source_file_name = source_file_name
        self.rdf_result_file_name = rdf_result_file_name
        self.rml_mapper = rml_mapper
        self.object_storage = object_storage
        self.triple_storage = triple_storage
        self.rml_rule = None
        self.data = None
        self.rdf_result = None

    def extract(self):
        """

        :return:
        """
        self.rml_rule = self.object_storage.get_object(
            object_name=f'{MINIO_RML_RULES_DIR}/{self.rml_rules_file_name}').decode('utf8')
        self.data = self.object_storage.get_object(
            object_name=f'{MINIO_RML_FIELDS_DIR}/{self.source_file_name}').decode('utf8')

    def transform(self):
        """

        :return:
        """
        assert self.rml_rule is not None
        assert self.data is not None
        self.rdf_result = []
        sources = {'ds_unified_sem_similarity_matrix.json': self.data}
        self.rdf_result = self.rml_mapper.transform(rml_rule=self.rml_rule, sources=sources)

    def load(self):
        """

        :return:
        """
        assert self.rdf_result is not None
        self.object_storage.put_object(object_name=f'{MINIO_RML_RESULTS_DIR}/{self.rdf_result_file_name}',
                                       content=self.rdf_result.encode('utf8'))
        self.triple_storage.create_dataset(dataset_id=DATASET_INDEX_NAME)
        self.triple_storage.upload_triples(dataset_id=DATASET_INDEX_NAME, quoted_triples=self.rdf_result,
                                           rdf_fmt=RDF_RESULT_FORMAT)

    def execute(self):
        """

        :return:
        """
        self.extract()
        self.transform()
        self.load()

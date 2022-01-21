import json
import logging
from sem_covid.adapters.abstract_store import ObjectStoreABC, TripleStoreABC
from sem_covid.adapters.rml_mapper import RMLMapperABC

MINIO_RML_RULES_DIR = 'rml_rules'
MINIO_RML_RESULTS_DIR = 'results'
MINIO_RML_FIELDS_DIR = 'fields'
DATASET_INDEX_NAME = 'ds_unified_topics'
RDF_RESULT_FORMAT = 'nt11'
CHUNK_SIZE = 100

logger = logging.getLogger(__name__)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


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
        self.rdf_results = None
        self.topic_assignments_data = None
        self.topics_data = None
        self.topic_tokens_data = None

    def extract(self):
        """

        :return:
        """
        self.rml_rule = self.object_storage.get_object(
            object_name=f'{MINIO_RML_RULES_DIR}/{self.rml_rules_file_name}').decode('utf8')
        self.topic_assignments_data = json.loads(self.object_storage.get_object(
            object_name=f'{MINIO_RML_FIELDS_DIR}/topic_assignments_data.json').decode('utf8'))
        self.topics_data = json.loads(self.object_storage.get_object(
            object_name=f'{MINIO_RML_FIELDS_DIR}/topics_data.json').decode('utf8'))
        self.topic_tokens_data = json.loads(self.object_storage.get_object(
            object_name=f'{MINIO_RML_FIELDS_DIR}/topic_tokens_data.json').decode('utf8'))
        logger.info("Load data with success!")

    def transform(self):
        """

        :return:
        """
        assert self.rml_rule is not None
        assert self.topic_assignments_data is not None
        assert self.topics_data is not None
        assert self.topic_tokens_data is not None

        self.rdf_results = []

        process_order = [
            ('topic_assignments_data', self.topic_assignments_data),
            ('topics_data', self.topics_data),
            ('topic_tokens_data', self.topic_tokens_data),
        ]
        self.triple_storage.create_dataset(dataset_id=DATASET_INDEX_NAME)
        for process_name, process_data in process_order:
            logger.info(f"Start processing : {process_name}")
            print(f"Start processing : {process_name}")
            for chunk in chunks(process_data, CHUNK_SIZE):
                topic_data_mapping = {process_name: chunk}
                sources = {'topics_data.json': json.dumps(topic_data_mapping)}
                logger.info("Start transform")
                rdf_result = self.rml_mapper.transform(rml_rule=self.rml_rule, sources=sources)
                logger.info("End transform")
                logger.info("Start load in fuseki")
                self.triple_storage.upload_triples(dataset_id=DATASET_INDEX_NAME, quoted_triples=rdf_result,
                                                   rdf_fmt=RDF_RESULT_FORMAT)
                logger.info("End load in fuseki")
                del rdf_result

        logger.info("End transformation step!")

    def load(self):
        """

        :return:
        """

    def execute(self):
        """

        :return:
        """
        self.extract()
        self.transform()
        self.load()

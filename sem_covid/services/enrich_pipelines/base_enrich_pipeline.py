import pandas as pd
from gensim.models import KeyedVectors

from sem_covid.services.data_registry import LanguageModel
from sem_covid.services.store_registry import StoreRegistry
from sem_covid.services.model_registry import ClassificationModel

EMBEDDING_COLUMN = "embeddings"


class BasePrepareDatasetPipeline:

    def __init__(self, ds_es_index: str, features_store_name: str):
        self.ds_es_index = ds_es_index
        self.features_store_name = features_store_name
        self.dataset = pd.DataFrame()
        self.l2v_dict = {}

    def load_dataset(self):
        es_store = StoreRegistry.es_index_store()
        self.dataset = es_store.get_dataframe(self.ds_es_index)
        assert self.dataset is not None
        assert len(self.dataset) > 0

    def load_language_models(self):
        law2vec = LanguageModel.LAW2VEC.fetch()
        law2vec_path = LanguageModel.LAW2VEC.path_to_local_cache()
        law2vec_format = KeyedVectors.load_word2vec_format(law2vec_path, encoding="utf-8")
        self.l2v_dict = {w: vec for w, vec in zip(law2vec_format.index_to_key, law2vec_format.vectors)}

    def prepare_textual_columns(self):
        raise NotImplementedError

    def create_embeddings(self):
        raise NotImplementedError

    def store_features(self):
        assert EMBEDDING_COLUMN in self.dataset
        feature_store = StoreRegistry.es_feature_store()
        input_features_name = self.features_store_name + '_x'
        matrix_df = pd.DataFrame(list(self.dataset[EMBEDDING_COLUMN].values))
        feature_store.put_features(features_name=input_features_name, content=matrix_df)

    def execute(self):
        self.load_dataset()
        self.load_language_models()
        self.prepare_textual_columns()
        self.create_embeddings()
        self.store_features()


class BaseEnrichPipeline:

    def __init__(self, feature_store_name: str, ds_es_index: str, class_names: list, experiment_ids: list):
        self.feature_store_name = feature_store_name
        self.ds_es_index = ds_es_index
        self.class_names = class_names
        self.experiments_ids = experiment_ids
        self.models = {}
        self.features = []
        self.dataset = pd.DataFrame()

    def load_dataset(self):
        es_store = StoreRegistry.es_index_store()
        dataset = es_store.get_dataframe(index_name=self.ds_es_index)
        assert dataset is not None
        assert len(dataset) > 0
        self.dataset = dataset

    def load_features(self):
        input_features_name = self.feature_store_name + '_x'
        feature_store = StoreRegistry.es_feature_store()
        input_features_name = feature_store.get_features(features_name=input_features_name)
        assert input_features_name is not None
        assert len(input_features_name) > 0
        self.features = input_features_name.values.tolist()

    def load_ml_flow_models(self):
        self.models = {}
        for class_name in self.class_names:
            self.models[class_name] = ClassificationModel.pwdb_by_class_name(class_name=class_name)

    def enrich_dataset(self):
        for class_name in self.class_names:
            model = self.models[class_name]
            self.dataset[class_name] = model.predict(list(self.features))

    def store_dataset_in_es(self):
        for class_name in self.class_names:
            assert class_name in self.dataset.columns
        es_client = StoreRegistry.es_index_store()
        new_index_name = self.ds_es_index + '_enriched'
        self.dataset.reset_index(drop=True, inplace=True)
        es_client.put_dataframe(index_name=new_index_name, content=self.dataset)

    def execute(self):
        self.load_dataset()
        self.load_features()
        self.load_ml_flow_models()
        self.enrich_dataset()
        self.store_dataset_in_es()

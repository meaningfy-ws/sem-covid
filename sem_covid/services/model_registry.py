#!/usr/bin/python3

# model_registry.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to provide a simple access mechanism to the previously trained model and stored in MlFlow.
     The realization of this mechanism is done through a register of models.
"""

import mlflow
import spacy
from gensim.models import KeyedVectors
from mlflow.sklearn import load_model
from abc import ABC, abstractmethod

from sem_covid.adapters.abstract_model import WordEmbeddingModelABC, SentenceEmbeddingModelABC, TokenizerModelABC, \
    DocumentEmbeddingModelABC
from sem_covid.adapters.embedding_models import SpacyTokenizerModel, BasicTokenizerModel, Word2VecEmbeddingModel, \
    AverageSentenceEmbeddingModel, TfIdfSentenceEmbeddingModel, UniversalSentenceEmbeddingModel, \
    EurLexBertSentenceEmbeddingModel, TfIdfDocumentEmbeddingModel, SpacySentenceSplitterModel
from sem_covid.services.data_registry import LanguageModel

BUSINESSES_CLASS_EXPERIMENT_ID = '12'
CITIZENS_CLASS_EXPERIMENT_ID = '13'
WORKERS_CLASS_EXPERIMENT_ID = '14'
CATEGORY_CLASS_EXPERIMENT_ID = '15'
SUBCATEGORY_CLASS_EXPERIMENT_ID = '20'
TYPE_OF_MEASURE_EXPERIMENT_ID = '21'
TARGET_GROUPS_EXPERIMENT_ID = '22'
FUNDING_EXPERIMENT_ID = '73'


def get_best_model_from_ml_flow(experiment_ids: list, metric_name: str = 'F1'):
    """
        This function aims to extract from MlFlow a model based on experiment_ids,
        where the model is selected according to the maximum metric, the name of which is transmitted by metric_name.

    :param experiment_ids: a list of ids of the experiments corresponding to a class
    :param metric_name: the name of the metric based on which the best model is selected
    :return: a trained machine learning model
    """
    runs_df = mlflow.search_runs(experiment_ids=experiment_ids, filter_string="tags.Source='finalize_model'")
    id_run = runs_df.loc[runs_df[f"metrics.{metric_name}"].idxmax()]['run_id']
    return load_model("runs:/" + id_run + "/model")


class ClassificationModel:
    """
        This Singleton class represents the pattern register,
         where patterns can be accessed based on class properties
          or through a pattern access method based on the classifier name.
    """

    @staticmethod
    def pwdb_by_class_name(class_name: str):
        """
            This method provides a model driven based on class_name.
        :param class_name: the name of the class on which the model was trained
        :return: returns from MlFlow an already trained machine learning model
        """

        class_name_to_exp_id = {
            'businesses': [BUSINESSES_CLASS_EXPERIMENT_ID],
            'citizens': [CITIZENS_CLASS_EXPERIMENT_ID],
            'workers': [WORKERS_CLASS_EXPERIMENT_ID],
            "category": [CATEGORY_CLASS_EXPERIMENT_ID],
            "subcategory": [SUBCATEGORY_CLASS_EXPERIMENT_ID],
            "type_of_measure": [TYPE_OF_MEASURE_EXPERIMENT_ID],
            "target_groups": [TARGET_GROUPS_EXPERIMENT_ID],
            'funding': [FUNDING_EXPERIMENT_ID]
        }
        if class_name in class_name_to_exp_id.keys():
            return get_best_model_from_ml_flow(experiment_ids=class_name_to_exp_id[class_name])
        else:
            return None

    @property
    def PWDB_BUSINESSES(self):
        return get_best_model_from_ml_flow(experiment_ids=[BUSINESSES_CLASS_EXPERIMENT_ID])

    @property
    def PWDB_CITIZENS(self):
        return get_best_model_from_ml_flow(experiment_ids=[CITIZENS_CLASS_EXPERIMENT_ID])

    @property
    def PWDB_WORKERS(self):
        return get_best_model_from_ml_flow(experiment_ids=[WORKERS_CLASS_EXPERIMENT_ID])

    @property
    def PWDB_CATEGORY(self):
        return get_best_model_from_ml_flow(experiment_ids=[CATEGORY_CLASS_EXPERIMENT_ID])

    @property
    def PWDB_SUBCATEGORY(self):
        return get_best_model_from_ml_flow(experiment_ids=[SUBCATEGORY_CLASS_EXPERIMENT_ID])

    @property
    def PWDB_TYPE_OF_MEASURE(self):
        return get_best_model_from_ml_flow(experiment_ids=[TYPE_OF_MEASURE_EXPERIMENT_ID])

    @property
    def PWDB_TARGET_GROUPS(self):
        return get_best_model_from_ml_flow(experiment_ids=[TARGET_GROUPS_EXPERIMENT_ID])

    @property
    def PWDB_FUNDING(self):
        return get_best_model_from_ml_flow(experiment_ids=[FUNDING_EXPERIMENT_ID])


class EmbeddingModelRegistryABC(ABC):

    @abstractmethod
    def word2vec_law(self) -> WordEmbeddingModelABC:
        raise NotImplementedError

    @abstractmethod
    def sent2vec_avg(self) -> SentenceEmbeddingModelABC:
        raise NotImplementedError

    @abstractmethod
    def sent2vec_tfidf_avg(self) -> SentenceEmbeddingModelABC:
        raise NotImplementedError

    @abstractmethod
    def sent2vec_universal_sent_encoding(self) -> SentenceEmbeddingModelABC:
        raise NotImplementedError

    @abstractmethod
    def sent2vec_eurlex_bert(self) -> SentenceEmbeddingModelABC:
        raise NotImplementedError


class TokenizerModelRegistryABC(ABC):

    @abstractmethod
    def basic_tokenizer(self) -> TokenizerModelABC:
        raise NotImplementedError

    @abstractmethod
    def spacy_tokenizer(self) -> TokenizerModelABC:
        raise NotImplementedError


class TokenizerModelRegistry(TokenizerModelRegistryABC):

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def spacy_tokenizer(self) -> TokenizerModelABC:
        return SpacyTokenizerModel(spacy_tokenizer=self.nlp.tokenizer)

    def basic_tokenizer(self) -> TokenizerModelABC:
        return BasicTokenizerModel()


class EmbeddingModelRegistry(EmbeddingModelRegistryABC):

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def word2vec_law(self) -> WordEmbeddingModelABC:
        LanguageModel.LAW2VEC.fetch()
        law2vec_path = LanguageModel.LAW2VEC.path_to_local_cache()
        l2v_dict = KeyedVectors.load_word2vec_format(law2vec_path, encoding="utf-8")
        return Word2VecEmbeddingModel(word2vec=l2v_dict)

    def sent2vec_avg(self) -> SentenceEmbeddingModelABC:
        return AverageSentenceEmbeddingModel(word_embedding_model=self.word2vec_law(),
                                             tokenizer=tokenizer_registry.spacy_tokenizer()
                                             )

    def sent2vec_tfidf_avg(self) -> SentenceEmbeddingModelABC:
        return TfIdfSentenceEmbeddingModel(word_embedding_model=self.word2vec_law(),
                                           tokenizer=tokenizer_registry.spacy_tokenizer()
                                           )

    def sent2vec_universal_sent_encoding(self) -> SentenceEmbeddingModelABC:
        return UniversalSentenceEmbeddingModel()

    def sent2vec_eurlex_bert(self) -> SentenceEmbeddingModelABC:
        return EurLexBertSentenceEmbeddingModel()

    def doc2vec_tfidf_weight_avg(self) -> DocumentEmbeddingModelABC:
        return TfIdfDocumentEmbeddingModel(sent_emb_model=UniversalSentenceEmbeddingModel(),
                                           sent_splitter=SpacySentenceSplitterModel(spacy_nlp=self.nlp),
                                           top_k=10)


tokenizer_registry = TokenizerModelRegistry()
embedding_registry = EmbeddingModelRegistry()

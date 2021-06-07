#!/usr/bin/python3

# pwdb_base_experiment.py
# Date:  22/03/2021
# Author: Chiriac Dan
# Email: dan.chiriac1453@gmail.com

"""
    Base class for all experiments performed on PDWB dataset using SVM algorithm.
    The common part to all ML experiments is the model training, model evaluation and model validation.
"""
import logging
import pickle

from gensim.models import KeyedVectors
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC, LinearSVC

from sem_covid.services.pwdb_base_experiment import PWDBBaseExperiment
from sem_covid.services.sc_wrangling.evaluation_metrics import model_evaluation_metrics
from sem_covid.services.sc_wrangling.mean_vectorizer import MeanEmbeddingVectorizer
from sem_covid.services.data_registry import LanguageModel

logger = logging.getLogger(__name__)

PWDB_TRAIN_TEST = 'train_test_split.pkl'
PWDB_WORD2VEC_MODEL = 'word2vec/df.model'

LAW2VEC_SVM_CATEGORY = 'law2vec/SVM/svm_cateogry.pkl'
LAW2VEC_SVM_SUBCATEGORY = 'law2vec/SVM/svm_subcateogry.pkl'
LAW2VEC_SVM_TOM = 'law2vec/SVM/svm_type_of_measure.pkl'
LAW2VEC_SVM_TG_L1 = 'law2vec/SVM/svm_target_groups_l1.pkl'


class SVMPWDBExperiment(PWDBBaseExperiment):
    """
        This class implements the SVM ML experiments
    """

    def __init__(self, minio_model_adapter, minio_adapter, requests, **kwargs):
        super().__init__(minio_adapter, requests, None, **kwargs)
        self.minio_model_adapter = minio_model_adapter

    def model_training(self, *args, **kwargs):
        train_test_dataset = pickle.loads(self.minio_adapter.get_object(PWDB_TRAIN_TEST))

        law2vec_path = LanguageModel.LAW2VEC.path_to_local_cache()
        law2vec_format = KeyedVectors.load_word2vec_format(law2vec_path, binary=True)

        l2v_dict = {w: vec for w, vec in zip(law2vec_format.index_to_key, law2vec_format.vectors)}

        svm_l2v = Pipeline([
            ("word2vec vectorizer", MeanEmbeddingVectorizer(l2v_dict)),
            ("SVM", SVC())])
        linear_svc_l2v = Pipeline([
            ("word2vec vectorizer", MeanEmbeddingVectorizer(l2v_dict)),
            ("Multi-label classifier", MultiOutputClassifier(LinearSVC()))])

        fit_l2v_category = svm_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Category'])
        fit_l2v_subcategory = svm_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Subcategory'])
        fit_l2v_tom = svm_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Type of measure'])
        fit_l2v_target_groups_l1 = linear_svc_l2v.fit(train_test_dataset['X_train'],
                                                      train_test_dataset['y_train'][
                                                          ['Businesses', 'Citizens', 'Workers']])

        pickle_l2v_category = pickle.dumps(fit_l2v_category)
        pickle_l2v_subcategory = pickle.dumps(fit_l2v_subcategory)
        pickle_l2v_tom = pickle.dumps(fit_l2v_tom)
        pickle_l2v_target_groups_l1 = pickle.dumps(fit_l2v_target_groups_l1)

        self.minio_adapter.put_object(LAW2VEC_SVM_CATEGORY, pickle_l2v_category)
        self.minio_adapter.put_object(LAW2VEC_SVM_SUBCATEGORY, pickle_l2v_subcategory)
        self.minio_adapter.put_object(LAW2VEC_SVM_TOM, pickle_l2v_tom)
        self.minio_adapter.put_object(LAW2VEC_SVM_TG_L1, pickle_l2v_target_groups_l1)

    def model_evaluation(self, *args, **kwargs):
        train_test_dataset = pickle.loads(self.minio_adapter.get_object(PWDB_TRAIN_TEST))

        l2v_category = pickle.loads(self.minio_adapter.get_object(LAW2VEC_SVM_CATEGORY))
        l2v_subcategory = pickle.loads(self.minio_adapter.get_object(LAW2VEC_SVM_SUBCATEGORY))
        l2v_tom = pickle.loads(self.minio_adapter.get_object(LAW2VEC_SVM_TOM))
        l2v_tg_l1 = pickle.loads(self.minio_adapter.get_object(LAW2VEC_SVM_TG_L1))

        l2v_category.score(train_test_dataset['X_train'], train_test_dataset['y_train']['Category'])
        l2v_subcategory.score(train_test_dataset['X_train'], train_test_dataset['y_train']['Subcategory'])
        l2v_tom.score(train_test_dataset['X_train'], train_test_dataset['y_train']['Type of measure'])
        l2v_tg_l1.score(train_test_dataset['X_train'],
                        train_test_dataset['y_train'][['Businesses', 'Citizens', 'Workers']])

        l2v_category_prediction = l2v_category.predict(train_test_dataset['X_test'])
        l2v_subcategory_prediction = l2v_subcategory.predict(train_test_dataset['X_test'])
        l2v_tom_prediction = l2v_tom.predict(train_test_dataset['X_test'])
        l2v_tg_l1_prediction = l2v_tg_l1.predict(train_test_dataset['X_test'])

        l2v_category_evaluation = model_evaluation_metrics(
            train_test_dataset['y_test']['Category'], l2v_category_prediction)
        l2v_subcategory_evaluation = model_evaluation_metrics(
            train_test_dataset['y_test']['Subcategory'], l2v_subcategory_prediction)
        l2v_tom_evaluation = model_evaluation_metrics(
            train_test_dataset['y_test']['Type of measure'], l2v_tom_prediction)
        l2v_tg_l1_evaluation = model_evaluation_metrics(
            train_test_dataset['y_test'][['Businesses', 'Citizens', 'Workers']], l2v_tg_l1_prediction)

    def model_validation(self, *args, **kwargs):
        pass

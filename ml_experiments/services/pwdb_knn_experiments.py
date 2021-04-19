#!/usr/bin/python3

# pwdb_base_experiment.py
# Date:  22/03/2021
# Author: Chiriac Dan
# Email: dan.chiriac1453@gmail.com

"""
    Base class for all experiments performed on PDWB dataset using KNN algorithm.
    The common part to all ML experiments is the model training, model evaluation and model validation.
"""

import logging
import pickle
import tempfile

from gensim.models import KeyedVectors
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier as KNC

from ml_experiments.adapters.minio_adapter import MinioAdapter
from ml_experiments.services.base_experiment import BaseExperiment
from ml_experiments.services.sc_wrangling.mean_vectorizer import MeanEmbeddingVectorizer
from ml_experiments.services.sc_wrangling.evaluation_metrics import model_evaluation_metrics

logger = logging.getLogger(__name__)

# TODO: get rid of all the constants in this file; use config file for that

ML_EXPERIMENTS_BUCKET_NAME = "ml-experiments"
LANGUAGE_MODEL_BUCKET_NAME = "language-models"

PWDB_TRAIN_TEST = 'train_test_split.pkl'
LAW2VEC_MODEL = 'law2vec/Law2Vec.200d.txt'
PWDB_WORD2VEC_MODEL = 'word2vec/df.model'

MINIO_ACCESS_KEY = '2zVld17bTfKk8iu0Eh9H74MywAeDV3WQ'
MINIO_SECRET_KEY = 'ddk9fixfI9qXiMaZu1p2a7BsgY2yDopm'
MINIO_URL = 'srv.meaningfy.ws:9000'

WORD2VEC_SVM_CATEGORY = 'word2vec/SVM/svm_cateogry.pkl'
WORD2VEC_SVM_SUBCATEGORY = 'word2vec/SVM/svm_subcateogry.pkl'
WORD2VEC_SVM_TOM = 'word2vec/SVM/svm_type_of_measure.pkl'
WORD2VEC_SVM_TG_L1 = 'word2vec/SVM/svm_target_groups_l1.pkl'

LAW2VEC_SVM_CATEGORY = 'law2vec/SVM/svm_cateogry.pkl'
LAW2VEC_SVM_SUBCATEGORY = 'law2vec/SVM/svm_subcateogry.pkl'
LAW2VEC_SVM_TOM = 'law2vec/SVM/svm_type_of_measure.pkl'
LAW2VEC_SVM_TG_L1 = 'law2vec/SVM/svm_target_groups_l1.pkl'


class KNNPWDBExperiment(BaseExperiment):

    def data_extraction(self, *args, **kwargs):
        pass

    def data_validation(self, *args, **kwargs):
        pass

    def data_preparation(self, *args, **kwargs):
        pass

    def model_training(self, *args, **kwargs):
        minio_ml_experiments = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, ML_EXPERIMENTS_BUCKET_NAME)
        minio_language_model = MinioAdapter(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, LANGUAGE_MODEL_BUCKET_NAME)
        train_test_dataset = pickle.loads(minio_ml_experiments.get_object(PWDB_TRAIN_TEST))
        load_pwdb_word2vec = pickle.loads(minio_language_model.get_object(PWDB_WORD2VEC_MODEL))

        p = tempfile.NamedTemporaryFile()
        p.write(minio_language_model.get_object(LAW2VEC_MODEL))
        load_law2vec = KeyedVectors.load_word2vec_format(p.name)
        p.close()

        w2v_dict = {w: vec for w, vec in zip(load_pwdb_word2vec.wv.index2word, load_pwdb_word2vec.wv.syn0)}
        l2v_dict = {w: vec for w, vec in zip(load_law2vec.wv.index2word, load_law2vec.wv.syn0)}

        knn_w2v = Pipeline([
            ("word2vec vectorizer", MeanEmbeddingVectorizer(w2v_dict)),
            ("KNN", KNC())])

        knn_l2v = Pipeline([
            ("word2vec vectorizer", MeanEmbeddingVectorizer(l2v_dict)),
            ("KNN", KNC())])

        fit_w2v_category = knn_w2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Category'])
        fit_w2v_subcategory = knn_w2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Subcategory'])
        fit_w2v_tom = knn_w2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Type of measure'])
        fit_w2v_target_groups_l1 = knn_w2v.fit(train_test_dataset['X_train'],
                                               train_test_dataset['y_train'][['Businesses', 'Citizens', 'Workers']])

        fit_l2v_category = knn_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Category'])
        fit_l2v_subcategory = knn_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Subcategory'])
        fit_l2v_tom = knn_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['Type of measure'])
        fit_l2v_target_groups_l1 = knn_l2v.fit(train_test_dataset['X_train'],
                                               train_test_dataset['y_train'][['Businesses', 'Citizens', 'Workers']])

        pickle_w2v_category = pickle.dumps(fit_w2v_category)
        pickle_w2v_subcategory = pickle.dumps(fit_w2v_subcategory)
        pickle_w2v_tom = pickle.dumps(fit_w2v_tom)
        pickle_w2v_target_groups_l1 = pickle.dumps(fit_w2v_target_groups_l1)

        pickle_l2v_category = pickle.dumps(fit_l2v_category)
        pickle_l2v_subcategory = pickle.dumps(fit_l2v_subcategory)
        pickle_l2v_tom = pickle.dumps(fit_l2v_tom)
        pickle_l2v_target_groups_l1 = pickle.dumps(fit_l2v_target_groups_l1)

        minio_ml_experiments.put_object("word2vec/KNN/knn_cateogry.pkl", pickle_w2v_category)
        minio_ml_experiments.put_object("word2vec/KNN/knn_subcateogry.pkl", pickle_w2v_subcategory)
        minio_ml_experiments.put_object("word2vec/KNN/knn_type_of_measure.pkl", pickle_w2v_tom)
        minio_ml_experiments.put_object("word2vec/KNN/knn_target_groups_l1.pkl", pickle_w2v_target_groups_l1)

        minio_ml_experiments.put_object("law2vec/KNN/knn_cateogry.pkl", pickle_l2v_category)
        minio_ml_experiments.put_object("law2vec/KNN/knn_subcateogry.pkl", pickle_l2v_subcategory)
        minio_ml_experiments.put_object("law2vec/KNN/knn_type_of_measure.pkl", pickle_l2v_tom)
        minio_ml_experiments.put_object("law2vec/KNN/knn_target_groups_l1.pkl", pickle_l2v_target_groups_l1)

    def model_evaluation(self, *args, **kwargs):
        pass

    def model_validation(self, *args, **kwargs):
        pass















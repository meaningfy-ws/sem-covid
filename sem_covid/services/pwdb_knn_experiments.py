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

from sem_covid import config
from sem_covid.adapters.minio_adapter import MinioAdapter
from sem_covid.services.pwdb_base_experiment import PWDBBaseExperiment
from sem_covid.services.sc_wrangling.mean_vectorizer import MeanEmbeddingVectorizer
from sem_covid.services.sc_wrangling.evaluation_metrics import model_evaluation_metrics

logger = logging.getLogger(__name__)

PWDB_TRAIN_TEST = 'train_test_split.pkl'
PWDB_WORD2VEC_MODEL = 'word2vec/df.model'

WORD2VEC_KNN_CATEGORY = "word2vec/KNN/knn_cateogry.pkl"
WORD2VEC_KNN_SUBCATEGORY = "word2vec/KNN/knn_subcateogry.pkl"
WORD2VEC_KNN_TOM = "word2vec/KNN/knn_type_of_measure.pkl"
WORD2VEC_KNN_TG_L1 = "word2vec/KNN/knn_target_groups_l1.pkl"

LAW2VEC_KNN_CATEGORY = "law2vec/KNN/knn_cateogry.pkl"
LAW2VEC_KNN_SUBCATEGORY = "law2vec/KNN/knn_subcateogry.pkl"
LAW2VEC_KNN_TOM = "law2vec/KNN/knn_type_of_measure.pkl"
LAW2VEC_KNN_TG_L1 = "law2vec/KNN/knn_target_groups_l1.pkl"



class KNNPWDBExperiment(PWDBBaseExperiment):

    def model_training(self, *args, **kwargs):
        minio_ml_experiments = MinioAdapter(config.MINIO_URL, config.MINIO_ACCESS_KEY,
                                            config.MINIO_SECRET_KEY, config.ML_EXPERIMENTS_BUCKET_NAME)
        minio_language_model = MinioAdapter(config.MINIO_URL, config.MINIO_ACCESS_KEY,
                                            config.MINIO_SECRET_KEY, config.LANGUAGE_MODEL_BUCKET_NAME)
        train_test_dataset = pickle.loads(minio_ml_experiments.get_object(PWDB_TRAIN_TEST))
        load_pwdb_word2vec = pickle.loads(minio_language_model.get_object(PWDB_WORD2VEC_MODEL))

        p = tempfile.NamedTemporaryFile()
        p.write(minio_language_model.get_object(config.LAW2VEC_MODEL_PATH))
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

        minio_ml_experiments.put_object(WORD2VEC_KNN_CATEGORY, pickle_w2v_category)
        minio_ml_experiments.put_object(WORD2VEC_KNN_SUBCATEGORY, pickle_w2v_subcategory)
        minio_ml_experiments.put_object(WORD2VEC_KNN_TOM, pickle_w2v_tom)
        minio_ml_experiments.put_object(WORD2VEC_KNN_TG_L1, pickle_w2v_target_groups_l1)

        minio_ml_experiments.put_object(LAW2VEC_KNN_CATEGORY, pickle_l2v_category)
        minio_ml_experiments.put_object(LAW2VEC_KNN_SUBCATEGORY, pickle_l2v_subcategory)
        minio_ml_experiments.put_object(LAW2VEC_KNN_TOM, pickle_l2v_tom)
        minio_ml_experiments.put_object(LAW2VEC_KNN_TG_L1, pickle_l2v_target_groups_l1)

    def model_evaluation(self, *args, **kwargs):
        pass

    def model_validation(self, *args, **kwargs):
        pass















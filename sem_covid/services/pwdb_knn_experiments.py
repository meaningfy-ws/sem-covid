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
from sem_covid.services.data_registry import LanguageModel

logger = logging.getLogger(__name__)

PWDB_TRAIN_TEST = 'train_test_split.pkl'

LAW2VEC_KNN_CATEGORY = "law2vec/KNN/knn_cateogry.pkl"
LAW2VEC_KNN_SUBCATEGORY = "law2vec/KNN/knn_subcateogry.pkl"
LAW2VEC_KNN_TOM = "law2vec/KNN/knn_type_of_measure.pkl"
LAW2VEC_KNN_TG_L1 = "law2vec/KNN/knn_target_groups_l1.pkl"


class KNNPWDBExperiment(PWDBBaseExperiment):

    def model_training(self, *args, **kwargs):
        minio_ml_experiments = MinioAdapter(config.ML_EXPERIMENTS_BUCKET_NAME, config.MINIO_URL,
                                            config.MINIO_ACCESS_KEY, config.MINIO_SECRET_KEY)
        train_test_dataset = pickle.loads(minio_ml_experiments.get_object(PWDB_TRAIN_TEST))

        law2vec = LanguageModel.LAW2VEC.fetch()
        law2vec_format = KeyedVectors.load_word2vec_format(law2vec, binary=True)

        l2v_dict = {w: vec for w, vec in zip(law2vec_format.index_to_key, law2vec_format.vectors)}

        knn_l2v = Pipeline([
            ("word2vec vectorizer", MeanEmbeddingVectorizer(l2v_dict)),
            ("KNN", KNC())])

        fit_l2v_category = knn_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['category'])
        fit_l2v_subcategory = knn_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['subcategory'])
        fit_l2v_tom = knn_l2v.fit(train_test_dataset['X_train'], train_test_dataset['y_train']['type_of_measure'])
        fit_l2v_target_groups_l1 = knn_l2v.fit(train_test_dataset['X_train'],
                                               train_test_dataset['y_train'][['businesses', 'citizens', 'workers']])

        pickle_l2v_category = pickle.dumps(fit_l2v_category)
        pickle_l2v_subcategory = pickle.dumps(fit_l2v_subcategory)
        pickle_l2v_tom = pickle.dumps(fit_l2v_tom)
        pickle_l2v_target_groups_l1 = pickle.dumps(fit_l2v_target_groups_l1)

        minio_ml_experiments.put_object(LAW2VEC_KNN_CATEGORY, pickle_l2v_category)
        minio_ml_experiments.put_object(LAW2VEC_KNN_SUBCATEGORY, pickle_l2v_subcategory)
        minio_ml_experiments.put_object(LAW2VEC_KNN_TOM, pickle_l2v_tom)
        minio_ml_experiments.put_object(LAW2VEC_KNN_TG_L1, pickle_l2v_target_groups_l1)

    def model_evaluation(self, *args, **kwargs):
        pass

    def model_validation(self, *args, **kwargs):
        pass















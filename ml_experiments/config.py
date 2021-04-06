#!/usr/bin/python3

# config.py
# Date:  01/04/2021
# Author: Chiriac Dan
# Email: dan.chiriac1453@gmail.com

"""
Project wide configuration file.
"""

import logging
import os


class MLExperimentsConfig:
    logger_name = 'ml-experiments'
    logger = logging.getLogger(logger_name)

    @property
    def MINIO_ACCESS_KEY(self) -> str:
        value = os.environ.get('MINIO_ACCESS_KEY')
        self.logger.debug(value)
        return value

    @property
    def MINIO_SECRET_KEY(self) -> str:
        value = os.environ.get('MINIO_SECRET_KEY')
        self.logger.debug(value)
        return value

    @property
    def MINIO_URL(self) -> str:
        value = os.environ.get('MINIO_URL')
        self.logger.debug(value)
        return value

    @property
    def ML_EXPERIMENTS_BUCKET_NAME(self) -> str:
        value = os.environ.get('ML_EXPERIMENTS_BUCKET_NAME')
        self.logger.debug(value)
        return value

    @property
    def LANGUAGE_MODEL_BUCKET_NAME(self) -> str:
        value = os.environ.get('LANGUAGE_MODEL_BUCKET_NAME')
        self.logger.debug(value)
        return value

    @property
    def ML_EXPERIMENTS_TEST_BUCKET_NAME(self) -> str:
        value = os.environ.get('ML_EXPERIMENTS_TEST_BUCKET_NAME')
        self.logger.debug(value)
        return value

    @property
    def SC_PWDB_JSON(self) -> str:
        value = os.environ.get('SC_PWDB_JSON')
        self.logger.debug(value)
        return value

    @property
    def SC_PWDB_DATA_FRAME(self) -> str:
        value = os.environ.get('SC_PWDB_DATA_FRAME')
        self.logger.debug(value)
        return value

    @property
    def PWDB_DATASET_URL(self) -> str:
        value = os.environ.get('PWDB_DATASET_URL')
        self.logger.debug(value)
        return value

    @property
    def PWDB_WORD2VEC_MODEL(self) -> str:
        value = os.environ.get('PWDB_WORD2VEC_MODEL')
        self.logger.debug(value)
        return value

    @property
    def LAW2VEC_MODEL(self) -> str:
        value = os.environ.get('LAW2VEC_MODEL')
        self.logger.debug(value)
        return value

    @property
    def PWDB_TRAIN_TEST(self) -> str:
        value = os.environ.get('PWDB_TRAIN_TEST')
        self.logger.debug(value)
        return value

    @property
    def WORD2VEC_SVM_CATEGORY(self) -> str:
        value = os.environ.get('WORD2VEC_SVM_CATEGORY')
        self.logger.debug(value)
        return value

    @property
    def WORD2VEC_SVM_SUBCATEGORY(self) -> str:
        value = os.environ.get('WORD2VEC_SVM_SUBCATEGORY')
        self.logger.debug(value)
        return value

    @property
    def WORD2VEC_SVM_TOM(self) -> str:
        value = os.environ.get('WORD2VEC_SVM_TOM')
        self.logger.debug(value)
        return value

    @property
    def WORD2VEC_SVM_TG_L1(self) -> str:
        value = os.environ.get('WORD2VEC_SVM_TG_L1')
        self.logger.debug(value)
        return value

    @property
    def LAW2VEC_SVM_CATEGORY(self) -> str:
        value = os.environ.get('WORD2VEC_SVM_TG_L1')
        self.logger.debug(value)
        return value

    @property
    def LAW2VEC_SVM_SUBCATEGORY(self) -> str:
        value = os.environ.get('WORD2VEC_SVM_TG_L1')
        self.logger.debug(value)
        return value

    @property
    def LAW2VEC_SVM_TOM(self) -> str:
        value = os.environ.get('WORD2VEC_SVM_TG_L1')
        self.logger.debug(value)
        return value

    @property
    def LAW2VEC_SVM_TG_L1(self) -> str:
        value = os.environ.get('WORD2VEC_SVM_TG_L1')
        self.logger.debug(value)
        return value


config = MLExperimentsConfig()

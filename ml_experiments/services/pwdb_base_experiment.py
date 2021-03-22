#!/usr/bin/python3

# pwdb_base_experiment.py
# Date:  22/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    Base class for all experiments performed on PDWB dataset.
    The common part to all ML experiments is tha data loading, extraction and preparation.
"""
import logging

from ml_experiments.services.base_experiment import BaseExperiment

logger = logging.getLogger(__name__)


class PWDBBaseExperiment(BaseExperiment):

    def data_extraction(self, *args, **kwargs):
        # TODO: implement me by loading PWDB data from elasticsearch
        raise NotImplementedError

    def data_validation(self, *args, **kwargs):
        # TODO: implement me by validating the returned index structure for a start,
        #  and then checking assertions discovered from EDA exercise.
        raise NotImplementedError

    def data_preparation(self, *args, **kwargs):
        # TODO: implement me by cleaning, preprocessing, engineering features, applying the available language
        #  models (own-word2vec, law2vec, jrc-word2vec, bert, etc.); and then performing the train-test split.
        raise NotImplementedError

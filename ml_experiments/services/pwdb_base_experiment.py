#!/usr/bin/python3

# pwdb_base_experiment.py
# Date:  22/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    Base class for all experiments performed on PDWB dataset
"""
from ml_experiments.services.base_experiment import BaseExperiment


class PWDBBaseExperiment(BaseExperiment):

    def data_extraction(self, *args, **kwargs):
        # TODO: implement me
        raise NotImplementedError

    def data_validation(self, *args, **kwargs):
        # TODO: implement me
        raise NotImplementedError

    def data_preparation(self, *args, **kwargs):
        # TODO: implement me
        raise NotImplementedError

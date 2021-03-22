#!/usr/bin/python3

# dummy_experiment.py
# Date:  20/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import logging

from ml_experiments.services.base_experiment import BaseExperiment

logger = logging.getLogger(__name__)


class DummyExperiment(BaseExperiment):
    """
        Dummy experiment
    """

    def data_extraction(self, *args, **kwargs):
        result = f"running data_extraction: {str(args)} {str(kwargs)} "
        logger.info(result)
        return result

    def data_preparation(self, *args, **kwargs):
        result = f"running data_preparation: {str(args)} {str(kwargs)} "
        logger.info(result)
        return result

    def data_validation(self, *args, **kwargs):
        result = f"running data_validation: {str(args)} {str(kwargs)} "
        logger.info(result)
        return result

    def model_training(self, *args, **kwargs):
        result = f"running model_training: {str(args)} {str(kwargs)} "
        logger.info(result)
        return result

    def model_evaluation(self, *args, **kwargs):
        result = f"running model_evaluation: {str(args)} {str(kwargs)} "
        logger.info(result)
        return result

    def model_validation(self, *args, **kwargs):
        result = f"running model_validation: {str(args)} {str(kwargs)} "
        logger.info(result)
        return result

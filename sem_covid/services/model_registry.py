#!/usr/bin/python3

# model_registry.py
# Date:  01/07/2021
# Author: Stratulat Ștefan

"""
    This module aims to provide a simple access mechanism to the previously trained model and stored in MlFlow.
     The realization of this mechanism is done through a register of models.
"""

import mlflow
from mlflow.sklearn import load_model

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

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

        :param class_name: the name of the class on which the model was trained
        :return: returns from MlFlow an already trained machine learning model
        """
        class_name_to_exp_id = {
            'businesses': ['12'],
            'citizens': ['13'],
            'workers': ['14'],
            "category": ['15'],
            "subcategory": ['20'],
            "type_of_measure": ['21'],
            "target_groups": ['22']
        }
        if class_name in class_name_to_exp_id.keys():
            return get_best_model_from_ml_flow(experiment_ids=class_name_to_exp_id[class_name])
        else:
            return None

    @property
    def PWDB_BUSINESSES(self):
        return get_best_model_from_ml_flow(experiment_ids=['12'])

    @property
    def PWDB_CITIZENS(self):
        return get_best_model_from_ml_flow(experiment_ids=['13'])

    @property
    def PWDB_WORKERS(self):
        return get_best_model_from_ml_flow(experiment_ids=['14'])

    @property
    def PWDB_CATEGORY(self):
        return get_best_model_from_ml_flow(experiment_ids=['15'])

    @property
    def PWDB_SUBCATEGORY(self):
        return get_best_model_from_ml_flow(experiment_ids=['20'])

    @property
    def PWDB_TYPE_OF_MEASURE(self):
        return get_best_model_from_ml_flow(experiment_ids=['21'])

    @property
    def PWDB_TARGET_GROUPS(self):
        return get_best_model_from_ml_flow(experiment_ids=['22'])

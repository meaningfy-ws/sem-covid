import mlflow


def get_best_model_from_ml_flow(experiment_ids: list, metric_name: str = 'F1'):
    runs_df = mlflow.search_runs(experiment_ids=experiment_ids, filter_string="tags.Source='finalize_model'")
    id_run = runs_df.loc[runs_df[f"metrics.{metric_name}"].idxmax()]['run_id']
    return mlflow.sklearn.load_model("runs:/" + id_run + "/model")


class ClassificationModel:

    @staticmethod
    def pwdb_by_class_name(class_name: str):
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

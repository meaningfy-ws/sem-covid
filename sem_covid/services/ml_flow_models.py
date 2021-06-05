from sem_covid import config
import mlflow


def get_best_model_from_ml_flow(experiment_ids: list, class_name: str, metric_name: str = 'F1-Score'):
    query = f"params.class_name='{class_name}'"
    runs_df = mlflow.search_runs(experiment_ids=experiment_ids, filter_string=query)
    id_run = runs_df.loc[runs_df[f"metrics.{metric_name}"].idxmax()]['run_id']
    return mlflow.sklearn.load_model("runs:/" + id_run + "/model")

import mlflow

if __name__ == '__main__':
    with mlflow.start_run():
        mlflow.log_param('b', 2)
        mlflow.log_metric('a', 1)
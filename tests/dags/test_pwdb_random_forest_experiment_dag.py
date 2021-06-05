from sem_covid.entrypoints.ml_dags.pwdb_random_forest_experiment_dag import DAG_NAME


def test_pwdb_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert airflow_dag_bag.import_errors == {}
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'dataset_preparation', 'dataset_enrichment'}.issubset(set(task_ids))


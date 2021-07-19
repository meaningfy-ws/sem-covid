from sem_covid.entrypoints.ml_dags.classifiers_dag import classifier_dag_name


def test_pwdb_random_forest_experiment_dag_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=classifier_dag_name)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'feature_engineering', 'model_training'}.issubset(set(task_ids))

    download_and_split_task = dag.get_task('feature_engineering')
    upstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.upstream_list))
    assert not upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, download_and_split_task.downstream_list))
    assert 'model_training' in downstream_task_ids

    execute_worker_dags_task = dag.get_task('model_training')
    upstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.upstream_list))
    assert 'feature_engineering' in upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, execute_worker_dags_task.downstream_list))
    assert not downstream_task_ids


def test_sample_dag(airflow_dag_bag):
    print(airflow_dag_bag.dags)
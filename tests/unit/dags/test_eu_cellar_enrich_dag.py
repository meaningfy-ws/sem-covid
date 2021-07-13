
from sem_covid.entrypoints.ml_dags.eu_cellar_enrich_dag import DAG_NAME


def test_eu_cellar_enrich_dag_has_two_tasks_and_order(airflow_dag_bag):
    dag = airflow_dag_bag.get_dag(dag_id=DAG_NAME)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'dataset_preparation', 'dataset_enrichment'}.issubset(set(task_ids))

    dataset_preparation = dag.get_task('dataset_preparation')
    upstream_task_ids = list(map(lambda task: task.task_id, dataset_preparation.upstream_list))
    assert not upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, dataset_preparation.downstream_list))
    assert 'dataset_enrichment' in downstream_task_ids

    dataset_enrichment = dag.get_task('dataset_enrichment')
    upstream_task_ids = list(map(lambda task: task.task_id, dataset_enrichment.upstream_list))
    assert 'dataset_preparation' in upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, dataset_enrichment.downstream_list))
    assert not downstream_task_ids

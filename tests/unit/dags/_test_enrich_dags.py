from sem_covid.entrypoints.ml_dags.enrich_dags import (EU_CELLAR_ENRICH_DAG_NAME, EU_TIMELINE_ENRICH_DAG_NAME,
                                                       IRELAND_TIMELINE_ENRICH_DAG_NAME)


def _test_enrich_dag(dag_bag, dag_name: str):
    dag = dag_bag.get_dag(dag_id=dag_name)
    assert dag is not None
    tasks = dag.tasks
    task_ids = list(map(lambda task: task.task_id, tasks))
    assert {'prepare_dataset', 'enrich_dataset'}.issubset(set(task_ids))

    dataset_preparation = dag.get_task('prepare_dataset')
    upstream_task_ids = list(map(lambda task: task.task_id, dataset_preparation.upstream_list))
    assert not upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, dataset_preparation.downstream_list))
    assert 'enrich_dataset' in downstream_task_ids

    dataset_enrichment = dag.get_task('enrich_dataset')
    upstream_task_ids = list(map(lambda task: task.task_id, dataset_enrichment.upstream_list))
    assert 'prepare_dataset' in upstream_task_ids
    downstream_task_ids = list(map(lambda task: task.task_id, dataset_enrichment.downstream_list))
    assert not downstream_task_ids


def test_eu_cellar_enrich_dag(airflow_dag_bag):
    _test_enrich_dag(airflow_dag_bag, EU_CELLAR_ENRICH_DAG_NAME)


def test_eu_timeline_enrich_dag(airflow_dag_bag):
    _test_enrich_dag(airflow_dag_bag, EU_TIMELINE_ENRICH_DAG_NAME)


def test_ireland_timeline_enrich_dag(airflow_dag_bag):
    _test_enrich_dag(airflow_dag_bag, IRELAND_TIMELINE_ENRICH_DAG_NAME)

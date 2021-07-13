#!/usr/bin/python3

# dag_factory.py
# Date:  19/05/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
     This module implements an automatic way of instantiation DAGs for ML and other types of Experiments.
"""
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator

from sem_covid.services import DEFAULTS_DAG_ARGS
from sem_covid.services.base_pipeline import BasePipeline

logger = logging.getLogger(__name__)

# TODO: move
def create_dag_pipeline(pipeline: BasePipeline, **dag_args):
    """
        This is an externalised factory method for all subclasses of BaseExperiment class.
    :param pipeline: an instance of an implementation of BaseExperiment.
    :param dag_args: any arguments that need to be passed onto DAG constructor
    :return: teh DAG object

    TODO: write an unit test for this function
    """
    updated_default_args_copy = {**DEFAULTS_DAG_ARGS.copy(), **dag_args.get('default_args', {})}
    dag_args['default_args'] = updated_default_args_copy
    dag_id = f"mlx_{pipeline.__class__.__name__}_{pipeline.version if pipeline.version else '0.0.1'}"
    print(dag_id)
    dag = DAG(dag_id=dag_id, **dag_args)
    with dag:
        # instantiate a PythonOperator for each ml stage
        stage_python_operators = [PythonOperator(task_id=f"{stage.__name__}_step",
                                                 python_callable=stage,
                                                 dag=dag)
                                  for stage in pipeline.pipeline_stages]
        # iterate stages in successive pairs and connect them
        for stage, successor_stage in zip(stage_python_operators, stage_python_operators[1:]):
            stage >> successor_stage
    return dag

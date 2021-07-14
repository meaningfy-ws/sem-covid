#!/usr/bin/python3

# abstract_dag_pipeline.py
# Date:  13/07/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc
from abc import abstractmethod


class DagPipeline(abc.ABC):
    """
        This abstract class offers a method that gets the steps of the DAG
    """
    @abstractmethod
    def get_steps(self) -> list:
        pass


class DagStep:
    """
        abstraction for DAG steps
    """
    def __init__(self, dag_pipeline: DagPipeline, dag_pipeline_step):
        self.dag_pipeline = dag_pipeline
        self.dag_pipeline_step = dag_pipeline_step

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass
import abc
import logging
from abc import abstractmethod

from airflow import DAG
from airflow.operators.python import PythonOperator

from sem_covid.adapters.dag.abstract_dag_pipeline import DagPipeline, DagStep
from sem_covid.entrypoints import DEFAULT_DAG_ARGUMENTS

logger = logging.getLogger(__name__)


class ObjectStateManager(abc.ABC):
    """
        This abstract class  saving and loading the object state. It needs to be pass against processes
        (this is the case in between airflow DAG steps) when this 2 functions can be used to pass the self objects
    """

    @abstractmethod
    def save_object_state(self, obj: object):
        pass

    @abstractmethod
    def load_object_state(self) -> object:
        pass


class StatefulDagStep(DagStep):
    """
        Abstracts steps that saves the states of previous actions
        By default use stateless pipeline.
    """

    def __init__(self, dag_pipeline: DagPipeline, dag_pipeline_step, object_state_manager: ObjectStateManager):
        super().__init__(dag_pipeline, dag_pipeline_step)
        self.object_state_manager = object_state_manager

    def __call__(self, *args, **kwargs):
        self.dag_pipeline = self.object_state_manager.load_object_state()
        getattr(self.dag_pipeline, self.dag_pipeline_step.__name__)(*args, **kwargs)
        self.object_state_manager.save_object_state(self.dag_pipeline)


class StatelessDagStep(DagStep):
    """
        Abstracts steps that does not save the previous states
    """

    def __call__(self, *args, **kwargs):
        getattr(self.dag_pipeline, self.dag_pipeline_step.__name__)(*args, **kwargs)


class DagFactory:
    """
        An automatic way of instantiation Airflow DAGs based on generic DAG pipelines.
        The schedule interval, max_active_runs, concurrency, retry, etc. shall be provided
        as either (a) default_dag_arguments, or (b) as arguments in create_dag method.
    """

    def __init__(self, dag_pipeline: DagPipeline, dag_name: str,
                 object_state_manager: ObjectStateManager = None,
                 default_dag_args: dict = DEFAULT_DAG_ARGUMENTS,
                 ):
        self.dag_name = dag_name
        self.default_args = default_dag_args
        self.dag_pipeline = dag_pipeline
        self.object_state_manager = object_state_manager

    def create_step(self, dag_pipeline_step) -> DagStep:
        """
            Generates steps for DAG Pipeline
            :dag_pipeline_step: steps of ETL DAGs
        """
        if self.object_state_manager:
            return StatefulDagStep(self.dag_pipeline, dag_pipeline_step, self.object_state_manager)
        else:
            return StatelessDagStep(self.dag_pipeline, dag_pipeline_step)

    def create_dag(self, **dag_args) -> DAG:
        """
            After finishing creating the steps, it creates the dag and deploys it.
        """

        with DAG(dag_id=self.dag_name, default_args=self.default_args, **dag_args) as dag:
            step_python_operators = [PythonOperator(task_id=f"{step.__name__}",
                                                    python_callable=self.create_step(step),
                                                    dag=dag)
                                     for step in self.dag_pipeline.get_steps()]

            for step, successor_step in zip(step_python_operators, step_python_operators[1:]):
                step >> successor_step
        logger.info(f"Instantiated DAG {self.dag_name}")
        return dag

import abc
from abc import abstractmethod

from airflow import DAG
from airflow.operators.python import PythonOperator


class DagPipeline(abc.ABC):

    @abstractmethod
    def get_steps(self) -> list:
        pass


class DagStep:
    def __init__(self, dag_pipeline: DagPipeline, dag_pipeline_step):
        self.dag_pipeline = dag_pipeline
        self.dag_pipeline_step = dag_pipeline_step

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class ObjectStateManager(abc.ABC):

    @abstractmethod
    def save_object_state(self, obj: object):
        pass

    @abstractmethod
    def load_object_state(self) -> object:
        pass


class DagPipelineManager:
    def __init__(self, dag_pipeline: DagPipeline, object_state_manager: ObjectStateManager = None):
        self.dag_pipeline = dag_pipeline
        self.object_state_manager = object_state_manager

    def create_step(self, dag_pipeline_step, stateful: bool = False) -> DagStep:
        if stateful:
            assert self.object_state_manager is not None
            return StatefulDagStep(self.dag_pipeline, dag_pipeline_step, self.object_state_manager)
        else:
            return StatelessDagStep(self.dag_pipeline, dag_pipeline_step)


class StatefulDagStep(DagStep):
    def __init__(self, dag_pipeline: DagPipeline, dag_pipeline_step, object_state_manager: ObjectStateManager):
        super().__init__(dag_pipeline, dag_pipeline_step)
        self.object_state_manager = object_state_manager

    def __call__(self, *args, **kwargs):
        self.dag_pipeline = self.object_state_manager.load_object_state()
        getattr(self.dag_pipeline, self.dag_pipeline_step.__name__)(*args, **kwargs)
        self.object_state_manager.save_object_state(self.dag_pipeline)


class StatelessDagStep(DagStep):
    def __call__(self, *args, **kwargs):
        getattr(self.dag_pipeline, self.dag_pipeline_step.__name__)(*args, **kwargs)


class DagFactory:

    def __init__(self, dag_manager: DagPipelineManager, dag_name: str, default_args: dict):
        self.dag_name = dag_name
        self.default_args = default_args
        self.dag_manager = dag_manager

    def create(self) -> DAG:
        dag_steps = self.dag_manager.dag_pipeline.get_steps()

        dag = DAG(self.dag_name, default_args=self.default_args, schedule_interval="@once", max_active_runs=1,
                  concurrency=4)
        current_step = PythonOperator(task_id=dag_steps[0].__name__,
                                      python_callable=self.dag_manager.create_step(dag_steps[0]), retries=1,
                                      dag=dag)
        for dag_step in dag_steps[1:]:
            next_step = PythonOperator(task_id=dag_step.__name__,
                                       python_callable=self.dag_manager.create_step(dag_step), retries=1, dag=dag)
            current_step >> next_step
            current_step = next_step

        return dag

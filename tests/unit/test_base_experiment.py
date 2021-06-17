from sem_covid.services.base_experiment import BaseExperiment


class FakeBaseExperiment(BaseExperiment):
    def data_extraction(self, *args, **kwargs):
        pass

    def data_validation(self, *args, **kwargs):
        pass

    def data_preparation(self, *args, **kwargs):
        pass

    def model_training(self, *args, **kwargs):
        pass

    def model_evaluation(self, *args, **kwargs):
        pass

    def model_validation(self, *args, **kwargs):
        pass


def test_base_experiment():
    experiment = FakeBaseExperiment()
    assert experiment.version == '0.0.1'
    experiment.data_extraction()
    experiment.data_validation()
    experiment.data_preparation()
    experiment.model_training()
    experiment.model_evaluation()
    experiment.model_validation()
    dag = experiment.create_dag()
    assert dag is not None

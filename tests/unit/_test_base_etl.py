from sem_covid.adapters.dag.base_etl_dag_pipeline import BaseETLPipeline


class FakeBaseETLPipeline(BaseETLPipeline):
    def load(self, *args, **kwargs):
        pass

    def extract(self, *args, **kwargs):
        pass

    def transform_structure(self, *args, **kwargs):
        pass

    def transform_content(self, *args, **kwargs):
        pass


def test_base_etl():
    etl = FakeBaseETLPipeline()
    assert etl.version == '0.0.1'
    etl.extract()
    etl.load()
    etl.transform_structure()
    etl.transform_content()
    # dag = etl.create_dag() # moved away
    # assert dag is not None

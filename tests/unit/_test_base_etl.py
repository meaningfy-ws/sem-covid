from sem_covid.services.base_etl import BaseETL


class FakeBaseETL(BaseETL):
    def load(self, *args, **kwargs):
        pass

    def extract(self, *args, **kwargs):
        pass

    def transform_structure(self, *args, **kwargs):
        pass

    def transform_content(self, *args, **kwargs):
        pass


def test_base_etl():
    etl = FakeBaseETL()
    assert etl.version == '0.0.1'
    etl.extract()
    etl.load()
    etl.transform_structure()
    etl.transform_content()
    dag = etl.create_dag()
    assert dag is not None

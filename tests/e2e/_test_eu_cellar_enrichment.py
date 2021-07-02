from sem_covid.services.enrich_pipelines.eu_cellar_enrich_pipeline import EuCellarEnrich


def test_dataset_preparation():
    EuCellarEnrich.prepare_dataset()


def test_dataset_enrichment():
    EuCellarEnrich.enrich_dataset()

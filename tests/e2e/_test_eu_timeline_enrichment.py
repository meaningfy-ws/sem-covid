from sem_covid.services.enrich_pipelines.eu_timeline_enrich_pipeline import EuTimeLineEnrich


def test_dataset_preparation():
    EuTimeLineEnrich.prepare_dataset()


def test_dataset_enrichment():
    EuTimeLineEnrich.enrich_dataset()

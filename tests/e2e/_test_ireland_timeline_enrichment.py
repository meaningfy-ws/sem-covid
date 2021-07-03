from sem_covid.services.enrich_pipelines.ireland_timeline_enrich_pipeline import IrelandTimeLineEnrich


def test_dataset_preparation():
    IrelandTimeLineEnrich.prepare_dataset()


def test_dataset_enrichment():
    IrelandTimeLineEnrich.enrich_dataset()

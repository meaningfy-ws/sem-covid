from sem_covid.entrypoints.ml_dags.enrich_dags import (enrich_eu_timeline_pipeline,
                                                       enrich_ireland_timeline_pipeline, enrich_eu_cellar_pipeline)


def test_eu_cellar_pipeline():
    eu_cellar_pipeline = enrich_eu_cellar_pipeline
    eu_cellar_pipeline.prepare_dataset()
    eu_cellar_pipeline.enrich_pipeline()


def test_eu_timeline_pipeline():
    eu_timeline_pipeline = enrich_eu_timeline_pipeline
    eu_timeline_pipeline.prepare_dataset()
    eu_timeline_pipeline.enrich_pipeline()


def test_ireland_pipeline():
    ireland_timeline_pipeline = enrich_ireland_timeline_pipeline
    ireland_timeline_pipeline.prepare_dataset()
    ireland_timeline_pipeline.enrich_pipeline()

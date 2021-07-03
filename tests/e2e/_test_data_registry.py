import pandas as pd

from sem_covid.services.data_registry import Dataset, LanguageModel


def test_pwdb_dataset():
    df = Dataset.PWDB.fetch()
    assert type(df) == pd.DataFrame
    assert len(df) > 0


def test_eu_cellar_dataset():
    df = Dataset.EU_CELLAR.fetch()
    assert type(df) == pd.DataFrame
    assert len(df) > 0


def test_eu_action_timeline_dataset():
    df = Dataset.EU_ACTION_TIMELINE.fetch()
    assert type(df) == pd.DataFrame
    assert len(df) > 0


def test_ireland_action_timeline():
    df = Dataset.IRELAND_ACTION_TIMELINE.fetch()
    assert type(df) == pd.DataFrame
    assert len(df) > 0


def test_law2vec_language_model():
    lm = LanguageModel.LAW2VEC.fetch()
    assert type(lm) == bytes
    assert len(lm) > 0


def test_jrc2vec_language_model():
    lm = LanguageModel.JRC2VEC.fetch()
    assert type(lm) == bytes
    assert len(lm) > 0


def test_eu_cellar_enriched_dataset():
    df = Dataset.EU_CELLAR_ENRICHED.fetch()
    assert type(df) == pd.DataFrame
    assert len(df) > 0


def test_eu_timeline_enriched_dataset():
    df = Dataset.EU_ACTION_TIMELINE_ENRICHED.fetch()
    assert type(df) == pd.DataFrame
    assert len(df) > 0


def test_ireland_timeline_enriched_dataset():
    df = Dataset.IRELAND_ACTION_TIMELINE_ENRICHED.fetch()
    assert type(df) == pd.DataFrame
    assert len(df) > 0

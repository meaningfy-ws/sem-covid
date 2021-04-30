import pytest

from sem_covid import config
import pandas as pd


def test_path_spoke_person():
    test_path = config.CRAWLER_EU_TIMELINE_SPOKEPERSONS
    assert test_path
    assert 'timeline_spoke' in test_path


def test_path_press_assistant():
    test_path = config.CRAWLER_EU_TIMELINE_PRESS_ASSISTANT
    assert test_path
    assert 'timeline_press' in test_path


def test_spoke_person_content():
    df_spoke_person = pd.read_json(config.CRAWLER_EU_TIMELINE_SPOKEPERSONS)
    spoke_person_name = 'Johannes Bahrke'
    assert not df_spoke_person.empty
    assert 'Name' in df_spoke_person.columns
    assert spoke_person_name in df_spoke_person['Name'].values
    assert df_spoke_person[df_spoke_person['Name'] == spoke_person_name]['Topics'][0]
    df_spoke_person['Name'] = df_spoke_person['Name'].apply(lambda x: x.lower())
    spoke_person_name_lwr = spoke_person_name.lower()
    assert spoke_person_name_lwr in df_spoke_person['Name'].values
    assert df_spoke_person[df_spoke_person['Name'] == spoke_person_name_lwr]['Topics'][0]

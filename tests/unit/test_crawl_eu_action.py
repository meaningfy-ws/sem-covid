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
    assert not df_spoke_person.empty
    assert 'Name' in df_spoke_person.columns
    assert 'Johannes Bahrke' in df_spoke_person['Name'].values
    assert df_spoke_person[df_spoke_person['Name'] == 'Johannes Bahrke']['Topics'][0]
    #assert df_spoke_person[df_spoke_person['Name'] == None]['Topics'][0]

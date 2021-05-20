
import logging

from sem_covid.services.sc_wrangling.json_transformer import transform_pwdb

logger = logging.getLogger(__name__)


def test_pwdb_transformer(raw_pwdb_data):
    assert len(raw_pwdb_data) == 2
    transformed_data_sample = transform_pwdb(raw_pwdb_data)[0]

    assert type(transformed_data_sample) == dict
    assert "title" in transformed_data_sample
    assert "country" in transformed_data_sample
    assert "occupations" in transformed_data_sample
    assert "Agricultural, forestry and fishery labourers" in transformed_data_sample['occupations']
    assert type(transformed_data_sample['occupations']) == list
    assert "sectors" in transformed_data_sample
    assert "03/27/2020" == transformed_data_sample["start_date"]
    assert "applications for phase" in transformed_data_sample["use_of_measure_description"]

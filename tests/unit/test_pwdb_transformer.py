
import logging

from ml_experiments.services.sc_wrangling.pwdb_transformer import transform_pwdb

logger = logging.getLogger(__name__)


def test_pwdb_transformer(raw_pwdb_data):
    assert len(raw_pwdb_data) == 2
    transformed_data_sample = transform_pwdb(raw_pwdb_data)[0]

    assert "Title" in transformed_data_sample
    assert "Country" in transformed_data_sample
    assert "03/27/2020" == transformed_data_sample["Start date"]
    assert "applications for phase" in transformed_data_sample["Use of measure"]


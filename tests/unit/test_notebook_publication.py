import os
from tests.unit.conftest import call_test_notebook, output_dir_for_converted_notebook
from sem_covid.services.sc_wrangling.notebook_publication import convert_notebook_to_html


def test_convert_notebook_to_html():
    convert = convert_notebook_to_html(call_test_notebook(), output_dir_for_converted_notebook())
    assert int == type(convert)

#!/usr/bin/python3

# test_dag_utils.py
# Date:  16/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from sem_covid.entrypoints import dag_name
from datetime import datetime


def test_dag_name():
    assert dag_name(category="a", name="a", role="a",
                    version_major=0, version_minor=0, version_patch=0,
                    versioning=True) == "a_a_a_0.0.0"
    assert dag_name(category="a", name="a", role="a",
                    version_major=0, version_minor=0, version_patch=0,
                    versioning=False) == "a_a_a"
    date_today = datetime.today().strftime('%Y-%m-%d')
    assert dag_name(category="a", name="a", role="a",
                    version_major=None, version_minor=0, version_patch=7,
                    versioning=True) == f"a_a_a_{date_today}(7)"
    assert dag_name(category="a", name="a") == f"a_a_0.1.0"

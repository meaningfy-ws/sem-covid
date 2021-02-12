#!/usr/bin/python3

# test_cellar_adapter.py
# Date:  11/02/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com
from adapters.cellar_adapter import CellarAdapter


def test_all_treaties_are_extracted():
    ca = CellarAdapter()

    treaties = ca.get_treaty_items()
    doc_ids = ca._extract_values(treaties, 'doc_id')

    assert len(doc_ids) == 45


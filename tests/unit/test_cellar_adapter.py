#!/usr/bin/python3

# test_cellar_adapter.py
# Date:  11/02/2021
# Author: Mihai Coșleț
# Email: coslet.mihai@gmail.com
from sem_covid.adapters.cellar_adapter import CellarAdapter


def test_all_treaties_are_extracted():
    ca = CellarAdapter()

    treaties = ca.get_treaty_items()
    treaty_titles = ca._extract_values(treaties, 'title')

    assert len(treaty_titles) == 45
    assert 'Charter of Fundamental Rights of the European Union' in treaty_titles
    assert '''Treaty between the Kingdom of Belgium, the Republic of Bulgaria, the Czech Republic, the Kingdom of Denmark, the Federal Republic of Germany, the Republic of Estonia, Ireland, the Hellenic Republic, the Kingdom of Spain, the French Republic, the Italian Republic, the Republic of Cyprus, the Republic of Latvia, the Republic of Lithuania, the Grand Duchy of Luxembourg, the Republic of Hungary, the Republic of Malta, the Kingdom of the Netherlands, the Republic of Austria, the Republic of Poland, the Portuguese Republic, Romania, the Republic of Slovenia, the Slovak Republic, the Republic of Finland, the Kingdom of Sweden, the United Kingdom of Great Britain and Northern Ireland (Member States of the European Union) and the Republic of Croatia concerning the accession of the Republic of Croatia to the European Union''' in treaty_titles

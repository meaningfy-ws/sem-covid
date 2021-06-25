#!/usr/bin/python3

# test_dag_bag.py
# Date:  15/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """


def test_imports(airflow_dag_bag):
    assert airflow_dag_bag.import_errors == {}

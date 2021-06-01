#!/usr/bin/python3

# __init__.py
# Date:  01/06/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import os
from pathlib import Path

TEST_AIRFLOW_DAG_FOLDER = Path(__file__).parent.parent.parent / "sem_covid/"
os.environ["AIRFLOW_HOME"] = str(TEST_AIRFLOW_DAG_FOLDER)

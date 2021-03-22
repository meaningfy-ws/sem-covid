#!/usr/bin/python3

# dummy_experiment_dag.py
# Date:  20/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

from datetime import datetime

from ml_experiments.services.dummy_experiment import DummyExperiment

dag = DummyExperiment().create_dag(start_date=datetime.now())
globals()[dag.dag_id] = dag

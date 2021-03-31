#!/usr/bin/python3

# dummy_experiment_dag.py
# Date:  29/03/2021
# Author: Dan Chiriac
# Email: dan.chiriac1453@gmail.com

""" """

from datetime import datetime

from ml_experiments.services.pwdb_svm_experiment import SVMPWDBExperiment

dag = SVMPWDBExperiment().create_dag(start_date=datetime.now())
globals()[dag.dag_id] = dag

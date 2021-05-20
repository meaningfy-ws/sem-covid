#!/usr/bin/python3

# dummy_experiment_dag.py
# Date:  29/03/2021
# Author: Dan Chiriac
# Email: dan.chiriac1453@gmail.com

""" """

from datetime import datetime

from sem_covid.services.pwdb_base_experiment import PWDBBaseExperiment

dag = PWDBBaseExperiment().create_dag(start_date=datetime.now())
globals()[dag.dag_id] = dag

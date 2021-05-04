#!/usr/bin/python3

# __init__.py
# Date:  18/03/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

"""

"""
from datetime import datetime

DEFAULTS_DAG_ARGS = {
    'owner': 'Meaningfy',
    'schedule_interval': '@once',
    "start_date": datetime.now(),
    'max_active_runs': 1,
    'concurrency': 1,
    "retries": 0,
    'depends_on_past': False,
}
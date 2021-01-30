#!/usr/bin/python3

# main.py
# Date:  30/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
from datetime import datetime

from adapters.pwdb_adapter import enrich_policy_watch, split_policy_watch

if __name__ == "__main__":
    print(str(datetime.now()) + " - starting downloading the EU’s PolicyWatch DB for Covid19 (JSON)...")
    enrich_policy_watch()
    split_policy_watch()
    print(str(datetime.now()) + " - done.")

#!/usr/bin/python3

# main.py
# Date:  30/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

from adapters.cellar_adapter import CellarAdapter

if __name__ == "__main__":
    # print(str(datetime.now()) + " - starting downloading the EU’s PolicyWatch DB for Covid19 (JSON)...")
    # enrich_policy_watch()
    # split_policy_watch()
    # print(str(datetime.now()) + " - done.")
    cellar_adapter = CellarAdapter()
    cellar_adapter.download_covid19_items()

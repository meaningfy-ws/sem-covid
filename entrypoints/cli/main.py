#!/usr/bin/python3

# main.py
# Date:  30/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
import json
import pathlib

from adapters.cellar_adapter import CellarAdapter

if __name__ == "__main__":
    # print(str(datetime.now()) + " - starting downloading the EU’s PolicyWatch DB for Covid19 (JSON)...")
    # enrich_policy_watch()
    # split_policy_watch()
    # print(str(datetime.now()) + " - done.")
    cellar_adapter = CellarAdapter()
    treaties_json = cellar_adapter.get_treaty_items()
    cellar_adapter.download_treaty_items(treaties_json)

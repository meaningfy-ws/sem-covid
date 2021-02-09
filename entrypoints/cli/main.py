#!/usr/bin/python3

# main.py
# Date:  30/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com
from adapters.cellar_adapter import CellarAdapter
from adapters.tika_adapter import TikaAdapter

if __name__ == "__main__":
    cellar_adapter = CellarAdapter()
    treaty_items = cellar_adapter.get_treaty_items()
    pass

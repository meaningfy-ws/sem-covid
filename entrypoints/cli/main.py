#!/usr/bin/python3

# main.py
# Date:  30/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

from adapters.tika_adapter import TikaAdapter

if __name__ == "__main__":
    tika = TikaAdapter()
    result = tika.parse_buffer('bla bla')

#!/usr/bin/python3

# cellar_adapter.py
# Date:  02/01/2021
# Author: Laurentiu Mandru
# Email: mclaurentiu79@gmail.com

from tika import parser

# TODO: provide a proper implementation

class TikaAdapter:
    def __init__(self, server_endpoint=None):
        self.__server_endpoint__ = server_endpoint

    def parse_buffer(self, buffer):
        if self.__server_endpoint__:
            result = parser.from_buffer(buffer, serverEndpoint=self.__server_endpoint__)
        else:
            result = parser.from_buffer(buffer)

        return result

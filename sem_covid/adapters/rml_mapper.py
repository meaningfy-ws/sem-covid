#!/usr/bin/python3

# rml_mapper.py
# Date:  13.12.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import json
from abc import ABC, abstractmethod
import requests


class RMLMapperABC(ABC):

    @abstractmethod
    def transform(self, rml_rule: str, sources: dict) -> str:
        pass


class RMLMapper(RMLMapperABC):

    def __init__(self,
                 rml_mapper_url: str
                 ):
        self.rml_mapper_url = rml_mapper_url

    def transform(self, rml_rule: str, sources: dict) -> str:
        rml_mapper_query = {"rml": rml_rule, "sources": sources}
        rml_mapper_result = requests.post(self.rml_mapper_url, json=rml_mapper_query)
        if rml_mapper_result.ok:
            return json.loads(rml_mapper_result.text)['output']
        else:
            print(rml_mapper_result)
            return None


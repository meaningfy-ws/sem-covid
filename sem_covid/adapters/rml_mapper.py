#!/usr/bin/python3

# rml_mapper.py
# Date:  13.12.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import json
from abc import ABC, abstractmethod
import requests


class RMLMapperABC(ABC):
    """
       This abstraction aims to create a uniform interface for different transformation engines
        that use RML as the mapping language.
    """

    @abstractmethod
    def transform(self, rml_rule: str, sources: dict) -> str:
        """
            This method aims to perform the transformation of some data sources based on the RML transformation rule.
        :param rml_rule: RML rule that will be used to transform data sources.
        :param sources: a dictionary with sources to be used in the transformation.
        :return: the result is a set of triplets in N3 format
        """
        pass


class RMLMapper(RMLMapperABC):
    """
        This class is a concrete implementation of an RML mapper that uses an external REST API.
    """

    def __init__(self,
                 rml_mapper_url: str
                 ):
        """
            Initialize class parameters.
        :param rml_mapper_url: url to a REST API that performs the logic of an RML mapper.
        """
        self.rml_mapper_url = rml_mapper_url

    def transform(self, rml_rule: str, sources: dict) -> str:
        """
            This method aims to perform the transformation of some data sources based on the RML transformation rule.
        :param rml_rule: RML rule that will be used to transform data sources.
        :param sources: a dictionary with sources to be used in the transformation.
        :return: the result is a set of triplets in N3 format
        """
        rml_mapper_query = {"rml": rml_rule, "sources": sources}
        rml_mapper_result = requests.post(self.rml_mapper_url, json=rml_mapper_query)
        if rml_mapper_result.ok:
            return json.loads(rml_mapper_result.text)['output']
        else:
            print(rml_mapper_result)
            return None


# -*- coding: utf-8 -*-
# Date    : 20.07.2021 
# Author  : Stratulat Ștefan
# File    : abstract_model.py
# Software: PyCharm
from abc import ABC, abstractmethod


class EmbeddingModelABC(ABC):

    @abstractmethod
    def encode(self, textual_units: list) -> list:
        raise NotImplementedError

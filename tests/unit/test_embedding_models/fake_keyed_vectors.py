# -*- coding: utf-8 -*-
# Date    : 20.07.2021 
# Author  : Stratulat Ștefan
# File    : fake_keyed_vectors.py
# Software: PyCharm
import numpy as np
from gensim.models import KeyedVectors


class FakeKeyedVectors(KeyedVectors):

    def __init__(self, vector_size: int):
        self.vector_size = vector_size
        self.data = dict()

    def __getitem__(self, key):
        if key not in self.data.keys():
            self.data[key] = np.random.rand(self.vector_size)
        return self.data[key]

    def __contains__(self, key):
        return True

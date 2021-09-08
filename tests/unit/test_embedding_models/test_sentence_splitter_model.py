#!/usr/bin/python3

# test_sentence_splitter_model.py
# Date:  07.09.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from sem_covid.adapters.embedding_models import BasicSentenceSplitterModel, SpacySentenceSplitterModel
from tests.unit.conftest import nlp


def test_basic_sentence_splitter_model():
    sent_splitter = BasicSentenceSplitterModel()
    text = 'Hello Siri! Hello Sam. Hello Jhon; Hello Adam?'
    text_splitted = sent_splitter.split(text)
    assert len(text_splitted) == 4
    assert text_splitted[0] == "Hello Siri!"
    assert text_splitted[1] == "Hello Sam."
    assert text_splitted[2] == "Hello Jhon;"
    assert text_splitted[3] == "Hello Adam?"


def test_spacy_sentence_splitter_model():
    sent_splitter = SpacySentenceSplitterModel(spacy_nlp=nlp)
    text = 'Hello Siri! Hello Sam. Hello Jhon; Hello Adam?'
    text_splitted = sent_splitter.split(text)
    assert len(text_splitted) == 3
    assert text_splitted[0] == "Hello Siri!"
    assert text_splitted[1] == "Hello Sam."
    assert text_splitted[2] == "Hello Jhon; Hello Adam?"

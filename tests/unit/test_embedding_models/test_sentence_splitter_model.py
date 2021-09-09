#!/usr/bin/python3

# test_sentence_splitter_model.py
# Date:  07.09.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

from sem_covid.adapters.embedding_models import BasicSentenceSplitterModel, SpacySentenceSplitterModel, \
    WindowedTextSplitterModel
from tests.unit.conftest import nlp

TEXT = 'Hello Siri! Hello Sam. Hello Jhon; Hello Adam?'


def test_basic_sentence_splitter_model():
    sent_splitter = BasicSentenceSplitterModel()

    text_splitted = sent_splitter.split(TEXT)
    assert len(text_splitted) == 4
    assert text_splitted[0] == "Hello Siri!"
    assert text_splitted[1] == "Hello Sam."
    assert text_splitted[2] == "Hello Jhon;"
    assert text_splitted[3] == "Hello Adam?"


def test_spacy_sentence_splitter_model():
    sent_splitter = SpacySentenceSplitterModel(spacy_nlp=nlp)
    text_splitted = sent_splitter.split(TEXT)
    assert len(text_splitted) >= 3


def test_windowed_sentence_splitter_model():
    sent_splitter = WindowedTextSplitterModel(sentence_splitter=BasicSentenceSplitterModel(),
                                              window_size=2, window_step=1
                                              )
    text_splitted = sent_splitter.split(TEXT)
    print(text_splitted)
    assert len(text_splitted) == 3
    assert text_splitted[0] == 'Hello Siri! Hello Sam.'
    assert text_splitted[1] == 'Hello Sam. Hello Jhon;'
    assert text_splitted[2] == 'Hello Jhon; Hello Adam?'

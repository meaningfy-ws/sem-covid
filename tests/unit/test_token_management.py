
import spacy
nlp = spacy.load("en_core_web_sm")

from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.token_management import *


def test_filter_stop_words():
    text = 'lorem ipsum and some stuff'
    doc = nlp(text)
    doc_without_stop_words = filter_stop_words(doc)

    assert list == type(doc_without_stop_words)
    assert len(doc_without_stop_words) == 3
    assert doc_without_stop_words[0].text == "lorem"
    assert doc_without_stop_words[1].text == "ipsum"
    assert doc_without_stop_words[2].text == "stuff"


def test_filter_pos():
    text = "lorem ipsum ."
    doc = nlp(text)
    doc_without_punct = filter_pos(doc, pos='PUNCT')

    assert list == type(doc_without_punct)
    assert len(doc_without_punct) == 2
    assert doc_without_punct[0].text == "lorem"
    assert doc_without_punct[1].text == "ipsum"


def test_select_pos():
    text = 'lorem ipsum and some stuff'
    doc = nlp(text)
    doc_nouns = select_pos(doc, "NOUN")

    assert list == type(doc_nouns)
    assert len(doc_nouns) == 2
    assert doc_nouns[0].text == "ipsum"
    assert doc_nouns[1].text == "stuff"


def test_filter_stop_words_on_a_span_list():
    text = "lorem ipsum and some stuff"
    doc = nlp(text)
    doc_noun_phrases = filter_stop_words_on_a_span_list(doc.noun_chunks)

    assert len(doc_noun_phrases) == 2
    assert ['lorem_ipsum', 'stuff'] == doc_noun_phrases


import spacy
nlp = spacy.load("en_core_web_sm")

from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.token_management import *


def test_filter_stop_words(spacy_document):
    doc_without_stop_words = filter_stop_words(spacy_document)

    assert list == type(doc_without_stop_words)
    assert len(doc_without_stop_words) == 3
    assert doc_without_stop_words[0].text == "moment"
    assert doc_without_stop_words[1].text == "happens"
    assert doc_without_stop_words[2].text == "."


def test_filter_pos(spacy_document):
    doc_without_punct = filter_pos(spacy_document, pos='PUNCT')

    assert list == type(doc_without_punct)
    assert len(doc_without_punct) == 5
    assert doc_without_punct[0].text == "That"
    assert doc_without_punct[1].text == "moment"
    assert doc_without_punct[2].text == "when"
    assert doc_without_punct[3].text == "that"
    assert doc_without_punct[4].text == "happens"


def test_select_pos(spacy_document):
    doc_nouns = select_pos(spacy_document, "NOUN")

    assert list == type(doc_nouns)
    assert len(doc_nouns) == 1
    assert doc_nouns[0].text == "moment"


def test_filter_stop_words_on_a_span_list(spacy_document):
    doc_noun_phrases = filter_stop_words_on_a_span_list(spacy_document.noun_chunks)

    assert len(doc_noun_phrases) == 1
    assert ['moment'] == doc_noun_phrases

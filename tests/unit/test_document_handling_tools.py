
import spacy
from spacy.tokens.doc import Doc

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.document_handling_tools import (
    document_atomization_noun_phrases, lemmatize_document)

nlp = spacy.load('en_core_web_sm')


def test_document_atomization_noun_phrases(spacy_document):
    sentence = "The Constitution of the United States is the supreme law of the United States of America."
    doc = nlp(sentence)

    atomized_document = document_atomization_noun_phrases(spacy_document)
    print(atomized_document)
    assert Doc == type(atomized_document)
    assert 'the_constitution' in atomized_document.text
    assert 'the_united_states' in atomized_document.text
    assert 'the_supreme_law' in atomized_document.text
    assert 'the_united_states' in atomized_document.text


def test_lemmatize_document(spacy_document):

    lemmatization = lemmatize_document(spacy_document)

    assert Doc == type(lemmatization)
    assert "['that', 'moment', 'when', 'that', 'happen', '.']" == str(lemmatization)

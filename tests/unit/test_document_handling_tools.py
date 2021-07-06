
import spacy
from spacy.tokens.doc import Doc

from sem_covid.entrypoints.notebooks.language_modeling.language_model_tools.document_handling_tools import document_atomization_noun_phrases

nlp = spacy.load('en_core_web_sm')


def test_document_atomization_noun_phrases():
    sentence = "The Constitution of the United States is the supreme law of the United States of America."
    doc = nlp(sentence)

    atomized_document = document_atomization_noun_phrases(doc)

    assert Doc == type(atomized_document)
    assert 'The_Constitution' in atomized_document.text
    assert 'the_United_States' in atomized_document.text
    assert 'the_supreme_law' in atomized_document.text
    assert 'the_United_States' in atomized_document.text


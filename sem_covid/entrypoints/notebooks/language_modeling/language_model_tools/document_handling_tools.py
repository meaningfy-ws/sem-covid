
import spacy
from spacy.tokens.doc import Doc

nlp = spacy.load('en_core_web_sm')


def document_atomization_noun_phrases(document: Doc):
    """
        Detects each noun phrase from inserted spacy document and transforms it
        into integrate single token
        :document: spacy document
        :return: The same document, but with atomized noun phrases
    """
    sentence = str(document)
    for noun_phrase in document.noun_chunks:
        sequence = str([x.lemma_ for x in noun_phrase])
        sentence = sentence.replace(sequence, sequence.replace(' ', '_'))
    return nlp(sentence)


def lemmatize_document(document: Doc) -> Doc:
    """
        Gets from the tokens in inserted document their lemma form
    """
    lemmatization = [word.lemma_ for word in document]
    return nlp(str(lemmatization))
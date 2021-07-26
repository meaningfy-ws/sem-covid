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
    sentence = str(document).lower()
    for noun_phrase in document.noun_chunks:
        noun_phrase_lemma = [x.lemma_ for x in noun_phrase]
        sequence = " ".join(
            [token for token in noun_phrase_lemma if token != "" and token != " "]).lower()
        sentence = sentence.replace(sequence, sequence.replace(' ', '_'))

    return nlp(sentence)


def lemmatize_document(document: Doc) -> Doc:
    """
        Gets from the tokens in inserted document their lemma form
    """
    lemmatization = [word.lemma_ for word in document]
    return nlp(str(lemmatization))

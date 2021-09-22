
import re

import spacy
import nltk
import enchant
from nltk.corpus import words
from spacy.tokens.doc import Doc
from gensim.parsing.preprocessing import remove_stopwords

en_words = set(words.words())
d = enchant.Dict("en_US")
nltk.download('words')
nlp = spacy.load('en_core_web_sm')


# def document_atomization_noun_phrases(document: Doc):
#     """
#         Detects each noun phrase from inserted spacy document and transforms it
#         into integrate single token
#         :document: spacy document
#         :return: The same document, but with atomized noun phrases
#     """
#     sentence = str(document).lower()
#     for noun_phrase in document.noun_chunks:
#         noun_phrase_lemma = [x.lemma_ for x in noun_phrase]
#         sequence = " ".join(
#             [token for token in noun_phrase_lemma if token != "" and token != " "]).lower()
#         sentence = sentence.replace(sequence, sequence.replace(' ', '_'))
#
#     return nlp(sentence)

def document_atomization_noun_phrases(document: Doc) -> str:
    """
        Detects each noun phrase from inserted spacy document and transforms it
        into integrate single token
        :document: spacy document
        :return: The same document, but with atomized noun phrases
    """
    sentence = ' '.join([word.lemma_ for word in document])
    for noun_phrase in document.noun_chunks:
        noun_phrase_lemma = [x.lemma_ for x in noun_phrase]
        sequence = " ".join(
            [token for token in noun_phrase_lemma if token != "" and token != " "])
        sequence_without_stopwords = remove_stopwords(sequence)
        sentence = sentence.replace(sequence, sequence_without_stopwords.replace(' ', '_'))

    return remove_stopwords(sentence)


def clean_text(text: str) -> str:
    tmp_word_list = re.sub(' +', ' ', re.sub(r'[^a-zA-Z_ ]', ' ', text)).lower().split(' ')
    result_words = [word
                    for word in tmp_word_list
                    if len(word) > 3 and (word in en_words or d.check(word))]
    if len(result_words) > 3:
        return ' '.join(result_words)
    else:
        return ''


def lemmatize_document(document: Doc) -> Doc:
    """
        Gets from the tokens in inserted document their lemma form
    """
    lemmatization = [word.lemma_ for word in document]
    return nlp(str(lemmatization))

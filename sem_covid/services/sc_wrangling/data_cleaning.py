import re
import string
import warnings

import pandas as pd
from cleantext import clean
import spacy

nlp = spacy.load("en_core_web_sm")


def clean_fix_unicode(text: str) -> str:
    return clean(text, fix_unicode=True, to_ascii=False, lower=False)


def clean_to_ascii(text: str) -> str:
    return clean(text, to_ascii=True, fix_unicode=False, lower=False)


def clean_to_lower(text: str) -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=True)


def clean_remove_line_breaks(text: str) -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=False, no_line_breaks=True)


def clean_remove_urls(text: str, replace_with: str = "<URL>") -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=False, no_urls=True, replace_with_url=replace_with)


def clean_remove_emails(text: str, replace_with: str = "<EMAIL>") -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=False, no_emails=True, replace_with_email=replace_with)


def clean_remove_numbers(text: str, replace_with: str = "<NUMBER>") -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=False, no_numbers=True,
                 replace_with_number=replace_with)


def clean_remove_digits(text: str, replace_with: str = "0") -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=False, no_digits=True, replace_with_digit=replace_with)


def clean_remove_punct(text: str, replace_with: str = "") -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=False, no_punct=True, replace_with_punct=replace_with)


def clean_remove_digits(text: str, replace_with: str = "0") -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=False, no_digits=True, replace_with_digit=replace_with)


def clean_remove_currency_symbols(text: str, replace_with: str = "<CUR>") -> str:
    return clean(text, fix_unicode=False, to_ascii=False, lower=False, no_currency_symbols=True,
                 replace_with_currency_symbol=replace_with)


def clean_remove_stopwords(text: str) -> str:
    stop_words = nlp.Defaults.stop_words
    return " ".join([word for word in text.split() if word not in stop_words])


def clean_text_from_specific_characters(document: pd.Series, characters: list) -> str:

    text = clean_remove_stopwords(str(document.values))

    for character in characters:
        if character in text:
            text = text.replace(character, "")

    return text


def prepare_text_for_cleaning(text: str):
    """
        assuming we have text that have to be cleaned
        to be used in training model. It will go through
        several stages of cleaning such as removing links,
        symbols, numbers i.e.
        :text: messy string, ready for cleaning
    """
    warnings.warn("", DeprecationWarning)
    stopword = nlp.Defaults.stop_words
    # set text to lowercase
    text = text.lower()
    # remove links
    text = re.sub(r"^https?:\/\/.*[\r\n]*", '', text)
    # remove "new line" symbol
    text = re.sub('\n', '', text)
    # Match every decimal digits and every character marked as letters in Unicode database
    text = re.sub('\w*\d\w*', '', text)
    # Delete square brackets
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[‘’“”…]', '', text)
    # remove punctuation
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = ''.join(text)
    text = re.split('\W+', text)
    text = [word for word in text if word not in stopword]

    return text

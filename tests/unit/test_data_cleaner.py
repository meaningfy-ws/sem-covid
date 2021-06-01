
from sem_covid.services.sc_wrangling.data_cleaning import *


def test_clean_fix_unicode():
    test = "Hello World\u2160"
    test = clean_fix_unicode(test)
    assert test == "Hello WorldⅠ"


def test_clean_to_ascii():
    test = "Hello ȘțȚĂÎ!"
    test = clean_to_ascii(test)
    assert test == "Hello StTAI!"


def test_clean_to_lower():
    test = "Hello World!"
    test = clean_to_lower(test)
    assert test == "hello world!"


def test_clean_remove_line_breaks():
    pass


def test_clean_remove_urls():
    test = "Hello http://www.google.com World!"
    test = clean_remove_urls(test,replace_with="")
    assert test == "Hello World!"


def test_clean_remove_emails():
    test = "Hello abibabu.babu@gogobu.dubu World!"
    test = clean_remove_emails(test, replace_with="")
    assert test == "Hello World!"


def test_clean_remove_numbers():
    test = "Hello 2032305 World!"
    test = clean_remove_numbers(test, replace_with="")
    assert test == "Hello World!"


def test_clean_remove_digits():
    test = "Hello 2020 World!"
    test = clean_remove_digits(test, replace_with="0")
    assert test == "Hello 0000 World!"


def test_clean_remove_punct():
    test = "Hello, World!"
    test = clean_remove_punct(test, replace_with="")
    assert test == "Hello World"


def test_clean_remove_currency_symbols():
    test = "Hello 400$ World!"
    test = clean_remove_currency_symbols(test, replace_with="")
    assert test == "Hello 400 World!"


def test_clean_remove_stopwords():
    test = "This is simple text for test!"
    test = clean_remove_stopwords(test)
    assert test == "This simple text test!"
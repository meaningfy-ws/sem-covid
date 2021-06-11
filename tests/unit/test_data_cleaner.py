
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
    test = "PC \n Master \r Race"
    test = clean_remove_line_breaks(test)
    assert "PC Master Race" == test


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
    text = "Hello 2020 World!"
    test_remove_digits = clean_remove_digits(text, replace_with="")
    test_replace_digits = clean_remove_digits(text, replace_with="0")
    assert test_replace_digits == "Hello 0000 World!"
    assert test_remove_digits == "Hello World!"


def test_clean_remove_punct():
    test = "Hello, World!"
    test = clean_remove_punct(test, replace_with="")
    assert test == "Hello World"


def test_clean_remove_currency_symbols():
    test = "Hello 400$ World!"
    test = clean_remove_currency_symbols(test, replace_with="")
    assert test == "Hello 400 World!"


def test_clean_remove_stopwords():
    short_test = "This is simple text for test!"
    medium_text = "i me my myself ... see some stopwords? It can't be"
    long_text = "This is simple text for test! And basically that is true. This is really a simple test"

    test_short_text = clean_remove_stopwords(short_test)
    test_medium_text = clean_remove_stopwords(medium_text)
    test_long_text = clean_remove_stopwords(long_text)

    assert test_short_text == "This simple text test!"
    assert test_medium_text == "... stopwords? It can't"
    assert test_long_text == "This simple text test! And basically true. This simple test"


def test_clean_text_from_specific_characters():
    characters = ["<", ">"]
    text = "there is > in < donezia"
    test = clean_text_from_specific_characters(text, characters)

    assert "<" and ">" not in test
    assert "there is in donezia" == test

import spacy
import pandas as pd

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.word_handling import *


def test_get_nlp_docs(transformed_pwdb_dataframe):
    nlp_docs = get_nlp_docs(transformed_pwdb_dataframe[['identifier', 'title']])
    
    assert type(nlp_docs) == list
    assert type(nlp_docs[0]) == spacy.tokens.doc.Doc
    assert type(nlp_docs[1]) == spacy.tokens.doc.Doc
    

def test_get_entity_words(transformed_pwdb_dataframe):
    entity_words = get_entity_words(transformed_pwdb_dataframe[['identifier', 'title']])
    
    assert type(entity_words) == pd.core.series.Series
    assert entity_words.dtype == object
    

def test_get_named_entities(transformed_pwdb_dataframe):
    entity_words = get_named_entities(transformed_pwdb_dataframe[['identifier', 'title']])
    
    assert type(entity_words) == pd.core.series.Series
    assert entity_words.dtype == object


def test_remove_stopwords(transformed_pwdb_dataframe):
    pwdb_stopwords = remove_stopwords(transformed_pwdb_dataframe['title'])
    
    assert type(pwdb_stopwords) == pd.core.series.Series
    assert type(pwdb_stopwords) != pd.core.frame.DataFrame
    assert type(pwdb_stopwords[0]) == str
    assert 'Hardship case fund: Safety net self-employed' == pwdb_stopwords[0]
    assert 'Hardship case fund: Safety net for self-employed' != pwdb_stopwords[0]
    assert 'State support tourism - Access finance' == pwdb_stopwords[1]
    assert 'State support for tourism - Access to finance' != pwdb_stopwords[1]


def test_calculate_tf_idf(transformed_pwdb_dataframe):
    pwdb_tf_idf = calculate_tf_idf(transformed_pwdb_dataframe, 'pwdb_word_title')
    
    assert type(pwdb_tf_idf) == pd.core.frame.DataFrame
    assert 'pwdb_word_title' in pwdb_tf_idf
    assert 'TF-IDF' in pwdb_tf_idf


def test_get_ngrams(transformed_pwdb_dataframe):
    ngrams = get_ngrams(transformed_pwdb_dataframe['title'], 3)
    
    assert type(ngrams) == pd.core.series.Series
    assert type(ngrams) != pd.core.frame.DataFrame
    assert "Hardship case fund:" == ngrams[0]
    assert "case fund: Safety" == ngrams[1]
    assert "fund: Safety net" == ngrams[2]
    assert "Safety net for" == ngrams[3]


def test_get_noun_phrases(transformed_pwdb_dataframe):
    pwdb_noun_phrases = get_noun_phrases(transformed_pwdb_dataframe['title'])
    
    assert type(pwdb_noun_phrases) == pd.core.series.Series
    assert type(pwdb_noun_phrases) != pd.core.frame.DataFrame
    assert 'Hardship case fund' == pwdb_noun_phrases[0]
    assert 'Safety net' == pwdb_noun_phrases[1]
    assert 'State support' == pwdb_noun_phrases[2]
    assert 'tourism' == pwdb_noun_phrases[3]
    

def test_get_words(transformed_pwdb_dataframe):
    pwdb_words = get_words(transformed_pwdb_dataframe['title'])
    
    assert type(pwdb_words) == pd.core.series.Series
    assert type(pwdb_words) != pd.core.frame.DataFrame
    assert 'Hardship' == pwdb_words[0]
    assert 'case' == pwdb_words[1]
    assert 'fund:' == pwdb_words[2]
    assert 'Safety' == pwdb_words[3]
    assert 'net' == pwdb_words[4]
    assert 'self-employed' == pwdb_words[5]
    assert 'State' == pwdb_words[6]
    assert 'support' == pwdb_words[7]
    assert 'tourism' == pwdb_words[8]
    assert '-' == pwdb_words[9]
    assert 'Access' == pwdb_words[10]
    assert 'finance' == pwdb_words[11]
    

def test_delete_punctuation():
    string = 'Hello !!! There, Ave. Maria ()'
    string_without_punctuation =  delete_punctuation(string)
    
    assert 'Hello There Ave Maria' == string_without_punctuation
    
    
def test_prepare_text_data(transformed_pwdb_dataframe):
    prepared_pwdb = prepare_text_data(transformed_pwdb_dataframe['title'])
    
    assert type(prepared_pwdb) == pd.core.series.Series
    assert type(prepared_pwdb) != pd.core.frame.DataFrame
    assert 'hardship case fund safety net for self-employed' == prepared_pwdb[0]
    assert 'state support for tourism - access to finance' == prepared_pwdb[1]

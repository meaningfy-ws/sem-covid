
import gensim
import numpy
import spacy

from sem_covid.services.sc_wrangling.data_cleaning import clean_text_from_specific_characters
from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.lda_modeling import WordsModeling

nlp = spacy.load("en_core_web_sm")


def test_word_modeling(transformed_pwdb_dataframe):
    pwdb_descriptive_data = transformed_pwdb_dataframe['title'].map(str) + ' ' + \
                            transformed_pwdb_dataframe['background_info_description'].map(str) + ' ' + \
                            transformed_pwdb_dataframe['content_of_measure_description'].map(str) + ' ' + \
                            transformed_pwdb_dataframe['use_of_measure_description'] + ' ' + \
                            transformed_pwdb_dataframe['involvement_of_social_partners_description']
    unused_characters = ["\\r", ">", "\n", "\\", "<", "''", "%", "...", "\'", '"', "(", "\n", "[", "]"]
    clean_text = clean_text_from_specific_characters(pwdb_descriptive_data, unused_characters)
    doc = nlp(clean_text)

    noun_phrases = [word.text for word in doc.noun_chunks]
    separated_noun_phrases = [[nouns] for nouns in noun_phrases]

    word_modeling = WordsModeling(separated_noun_phrases)
    lda_training = word_modeling.lda_model_training()

    assert gensim.corpora.dictionary.Dictionary == type(word_modeling.id2word)
    assert list == type(word_modeling.corpus)
    assert str == type(word_modeling.id2word[0])
    assert "Hardship case fund" == word_modeling.id2word[0]
    assert tuple == type(word_modeling.corpus[0][0])
    assert (0, 1) == word_modeling.corpus[0][0]
    assert gensim.models.ldamulticore.LdaMulticore == type(lda_training)
    assert numpy.ndarray == type(lda_training.get_topics())
    assert "Corona crisis" == lda_training.id2word.get(1)
    assert 10 == lda_training.num_topics
    assert 10 == lda_training.chunksize
    assert 10 == lda_training.passes
    assert 100 == lda_training.iterations




import gensim
import pytest
import spacy
import pandas

from sem_covid.services.sc_wrangling.data_cleaning import clean_text_from_specific_characters
from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.topic_visualizer import TopicInformation
from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.lda_modeling import WordsModeling

nlp = spacy.load("en_core_web_sm")


class TestTopicVisualizer:

    @pytest.fixture(autouse=True)
    def _insert_transformed_pwdb_dataframe(self, transformed_pwdb_dataframe):
        self._transformed_pwdb_dataframe = transformed_pwdb_dataframe

    def _instantiate_topic_information(self):
        pwdb_descriptive_data = self._transformed_pwdb_dataframe['title'].map(str) + ' ' + \
                                self._transformed_pwdb_dataframe['background_info_description'].map(str) + ' ' + \
                                self._transformed_pwdb_dataframe['content_of_measure_description'].map(str) + ' ' + \
                                self._transformed_pwdb_dataframe['use_of_measure_description'] + ' ' + \
                                self._transformed_pwdb_dataframe['involvement_of_social_partners_description']

        unused_characters = ["\\r", ">", "\n", "\\", "<", "''", "%", "...", "\'", '"', "(", "\n", "[", "]"]
        clean_text = clean_text_from_specific_characters(pwdb_descriptive_data, unused_characters)
        doc = nlp(clean_text)

        noun_phrases = [word.text for word in doc.noun_chunks]
        separated_noun_phrases = [[nouns] for nouns in noun_phrases]

        word_modeling = WordsModeling(separated_noun_phrases)
        lda_training = word_modeling.lda_model_training()

        return TopicInformation(lda_training, separated_noun_phrases)

    def test_topic_information_injection(self):
        assert gensim.corpora.dictionary.Dictionary == type(self._instantiate_topic_information().id2word)
        assert list == type(self._instantiate_topic_information().corpus)
        assert gensim.models.ldamulticore.LdaMulticore == type(self._instantiate_topic_information().lda_model)

    def test_format_topic_sentence(self):
        topic_visualizer = self._instantiate_topic_information().format_topic_sentences()

        assert pandas.core.frame.DataFrame == type(topic_visualizer)
        assert "Document Number" in topic_visualizer
        assert "Dominant Topic" in topic_visualizer
        assert "Topic Percentage Contribution" in topic_visualizer
        assert "Keywords" in topic_visualizer
        assert "Text" in topic_visualizer
        assert len(topic_visualizer) == 115
        assert topic_visualizer['Text'][0] == ['Hardship case fund']
        assert topic_visualizer['Text'][1] != "Corona crisis"
        assert set(topic_visualizer['Dominant Topic']) == {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0}
        assert topic_visualizer['Topic Percentage Contribution'][0] == 0.550000011920929
        assert set(topic_visualizer['Topic Percentage Contribution']) == {0.550000011920929}

    def test_select_most_illustrative_sentence(self):
        top_topic = self._instantiate_topic_information().select_most_illustrative_sentence()

        assert pandas.core.frame.DataFrame == type(top_topic)
        assert "Document Number" in top_topic
        assert "Topic Number" in top_topic
        assert "Topic Percentage Contribution" in top_topic
        assert "Keywords" in top_topic
        assert "Representative Text" in top_topic
        assert len(top_topic) == 10
        assert set(top_topic['Topic Number']) == {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0}
        assert set(top_topic["Topic Percentage Contribution"]) == {0.550000011920929}

    def test_attribute_topic_per_document(self):
        dominant_topics, topic_percentages = self._instantiate_topic_information().attribute_topic_per_document(end=-1)

        assert list == type(dominant_topics)
        assert list == type(topic_percentages)
        assert 114 == len(dominant_topics)
        assert 114 == len(topic_percentages)
        assert (0, 3) == dominant_topics[0]

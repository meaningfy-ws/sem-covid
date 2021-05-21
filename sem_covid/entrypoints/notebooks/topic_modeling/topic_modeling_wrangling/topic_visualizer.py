
from PIL.Image import Image

import pyLDAvis
pyLDAvis.enable_notebook()
import pyLDAvis.gensim_models

import pandas as pd
from gensim.models import LdaMulticore
from wordcloud import WordCloud

from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.lda_modeling import WordsModeling


class TopicInformation(WordsModeling):
    def __init__(self, lda_model: LdaMulticore, document: pd.Series):
        self.lda_model = lda_model
        super().__init__(document)

    def format_topic_sentences(self) -> pd.DataFrame:
        """
            ach document is composed of multiple topics. But, typically only one of the topics is dominant.
            The below code extracts this dominant topic for each sentence and shows the weight of the
            topic and the keywords in a nicely formatted output.
        """
        topic_df = pd.DataFrame()

        for index, row_list in enumerate(self.lda_model[self.corpus]):
            row = row_list[0] if self.lda_model.per_word_topics else row_list
            sorted_row = sorted(row, key=lambda x: (x[1]), reverse=True)

            for number_of_rows, (topic_number, prop_number) in enumerate(sorted_row):
                if number_of_rows == 0:
                    word_propositions = self.lda_model.show_topic(topic_number)
                    topic_keywords = ", ".join([word for word, prop in word_propositions])
                    topic_df = topic_df.append(pd.Series([int(topic_number), round(prop_number, 4),
                                                         topic_keywords]), ignore_index=True)
                else:
                    break

        topic_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']
        contents = pd.Series(self.document)

        return pd.concat([topic_df, contents], axis=1)

    def sort_dominant_topic(self) -> pd.DataFrame:
        df_dominant_topics = self.format_topic_sentences().reset_index()
        df_dominant_topics.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

        return df_dominant_topics

    def select_most_illustrative_sentence(self) -> pd.DataFrame:
        """
            gets the most exemplar sentence for each topic
        """
        sorted_topics = pd.DataFrame()
        grouped_sorted_topics = self.sort_dominant_topic().groupby('Dominant_Topic')

        for topic_number, groups in grouped_sorted_topics:
            sorted_topics = pd.concat(
                [sorted_topics, groups.sort_values(['Topic_Perc_Contrib'], ascending=False).head(1)], axis=0)

        sorted_topics.reset_index(drop=True, inplace=True)
        sorted_topics.columns = ['Document_No', 'Topic_Num', "Topic_Perc_Contrib", "Keywords", "Representative Text"]

        return sorted_topics.head(10)

    def visualize_lda_model(self) -> pyLDAvis:
        """
            it will be used pyLDAVis  to visualise the information contained in a topic model.
        """
        pyLDAvis.enable_notebook()

        return pyLDAvis.gensim_models.prepare(self.lda_model, self.corpus, dictionary=self.lda_model.id2word)


def generate_wordcloud(words: str, max_words: int = 500) -> Image:
    """
        creates a wordcloud with the words of input text
        and visualize them
    """
    wordcloud = WordCloud(background_color="white", max_words=max_words, width=600,
                          height=600, contour_width=3, contour_color='steelblue')
    cloud_generator = wordcloud.generate(words)

    return cloud_generator.to_image()


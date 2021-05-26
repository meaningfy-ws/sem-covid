
from typing import List
from PIL.Image import Image

import pyLDAvis
import pyLDAvis.gensim_models

import plotly.graph_objs as go
from plotly.offline import iplot

import pandas as pd
from gensim.models import LdaMulticore
from wordcloud import WordCloud

from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.lda_modeling import WordsModeling


class TopicInformation(WordsModeling):
    def __init__(self, lda_model: LdaMulticore, document: List):
        self.lda_model = lda_model
        super().__init__(document)

    def format_topic_sentences(self) -> pd.DataFrame:
        """
            Each document is composed of multiple topics. But, typically only one of the topics is dominant.
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

        topic_df.columns = ['Dominant Topic', 'Percentage Contribution', 'Topic Keywords']
        contents = pd.Series(self.document)

        df_dominant_topics = pd.concat([topic_df, contents], axis=1).reset_index()
        df_dominant_topics.columns = ['Document Number', 'Dominant Topic', 'Topic Percentage Contribution',
                                      'Keywords', 'Text']

        return df_dominant_topics

    def select_most_illustrative_sentence(self) -> pd.DataFrame:
        """
            gets the most exemplar sentence for each topic
        """
        sorted_topics = pd.DataFrame()
        grouped_sorted_topics = self.format_topic_sentences().groupby('Dominant Topic')

        for topic_number, groups in grouped_sorted_topics:
            sorted_topics = pd.concat(
                [sorted_topics, groups.sort_values(['Topic Percentage Contribution'], ascending=False).head(1)], axis=0)

        sorted_topics.reset_index(drop=True, inplace=True)
        sorted_topics.columns = ['Document Number', 'Topic Number', "Topic Percentage Contribution", "Keywords",
                                 "Representative Text"]

        return sorted_topics.head(10)

    def attribute_topic_per_document(self, start: int = 0, end: int = 1) -> tuple:
        """
            g
        """
        corpus_sel = self.corpus[start: end]
        dominant_topics = []
        topic_percentages = []

        for index, corpus in enumerate(corpus_sel):
            topic_percentage, wordid_topics, wordid_phivalues = self.lda_model[corpus]
            dominant_topic = sorted(topic_percentage, key=lambda x: x[1], reverse=True)[0][0]
            dominant_topics.append((index, dominant_topic))
            topic_percentages.append(topic_percentage)

        return dominant_topics, topic_percentages

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


def plotly_bar_chart_graphic(chart_title: str, x_axis: pd.DataFrame, y_axis,
                             x_axis_title: str, y_axis_title: str):
    """
    assuming we want to represent in graphic chart specific data
    :chart_title: graphic title
    :x_axis: our DataFrame we will use as x axis
    :y_axis: our DataFrame we will use as y axis
    :x_axis_title: the title for our x axis
    :y_axis_title: the title for our y axis
    :return: bar chart graphic
    """
    layout = {"title": chart_title,
              "xaxis": {"title": x_axis_title},
              "yaxis": {"title": y_axis_title}}

    trace = go.Bar(x = x_axis,
                   y = y_axis)

    figure = go.Figure(data=trace, layout=layout)
    iplot(figure)
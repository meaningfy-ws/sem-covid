
from PIL.Image import Image

import plotly.graph_objs as go
from plotly.offline import iplot
import pandas as pd
from wordcloud import WordCloud


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
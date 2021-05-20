
from PIL.Image import Image

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

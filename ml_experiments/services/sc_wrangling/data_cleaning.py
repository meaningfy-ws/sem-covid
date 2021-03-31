
import re
import string

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')


def prepare_text_for_cleaning(text: str):
    """
        assuming we have text that have to be cleaned
        to be used in training model. It will go through
        several stages of cleaning such as removing links,
        symbols, numbers i.e.
        :text: messy string, ready for cleaning
    """
    stopword = stopwords.words('english')
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

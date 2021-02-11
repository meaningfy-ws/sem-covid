import re
import string

from nltk.corpus import stopwords


def cleaning(text):
    """cleaner function"""
    stopword = stopwords.words('english')

    # set text to lowercase
    text.lower()
    # remove links
    re.sub(r"^https?:\/\/.*[\r\n]*", '', text)
    # remove "new line" symbol
    re.sub('\n', '', text)
    # Match every decimal digits and every character marked as letters in Unicode database
    re.sub('\w*\d\w*', '', text)
    # Delete square brackets
    re.sub('\[.*?\]', '', text)
    re.sub('[‘’“”…]', '', text)
    # remove punctuation
    re.sub('[%s]' % re.escape(string.punctuation), '', text)
    ''.join(text)
    re.split('\W+', text)
    text = [word for word in text if word not in stopword]

    return text


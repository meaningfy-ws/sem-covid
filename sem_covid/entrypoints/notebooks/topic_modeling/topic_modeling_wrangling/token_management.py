
from typing import List, Union

import spacy
from spacy.tokens import Token
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
nlp = spacy.load("en_core_web_sm")

auxiliary_verbs = {'do', 'does', 'did', 'has', 'have', 'had', 'is', 'am', 'are', 'was', 'were', 'be', 'being',
                   'been', 'may', 'must', 'might', 'should', 'could', 'would', 'shall', 'will', 'can'}
nlp.Defaults.stop_words |= auxiliary_verbs
spacy_stop_words = nlp.Defaults.stop_words


def filter_stop_words(doc: List[Token], stop_words: List[str] = spacy_stop_words) -> List[Token]:
    """
        turn a spacy Doc into a list of token and remove stop words
    """
    return [token for token in doc if str(token.lower_) not in stop_words]


def filter_pos(doc: Doc, pos: Union[str, List[str]]) -> List[Token]:
    """
        filter out tokens that have the provided POS
    """
    if isinstance(pos,str):
        poses = [pos]
    else:
        poses = pos
    return [token for token in doc if token.pos_ not in poses]


def select_pos(doc: Doc, pos: Union[str, List[str]]) -> List[str]:
    """
        select tokens that have the desired POS
    """
    if isinstance(pos, str):
        poses = [pos]
    else:
        poses = pos
    return [token for token in doc if token.pos_ in poses]


def filter_stop_words_on_a_span_list(span_list: List[Span],
                                     stop_words: List[str] = nlp.Defaults.stop_words) -> List[str]:
    """
        Spacy noun phrases are provided as a list of Spans.
        Some noun phrases contain stop words, and we want those removed.
    """
    return list(filter(None, ["_".join(map(str,
                                           [token.lemma_ for token in filter_stop_words(span, stop_words)]
                                           )) for span in span_list]))

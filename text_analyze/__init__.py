#! coding: utf-8
from pkg_resources import resource_filename

import nltk
import pymorphy

filename = resource_filename("text_analyze", "data/pymorphy")
morph = pymorphy.get_morph(
    filename,
    backend='cdb',
    check_prefixes=False,
    predict_by_prefix=False,
    predict_by_suffix=False,
    handle_EE=True
)
filename = resource_filename("text_analyze", "data/nltk/english.pickle")
tokenizer = nltk.data.load(filename)


def analyze_text(words, text, analyzers=[]):
    for analyzer in analyzers:
        for word in words:
            for sentence in text:
                analyzer.mark(word, sentence)

#! coding: utf-8
from pkg_resources import resource_filename

import nltk
import pymorphy2

morph = pymorphy2.MorphAnalyzer()
filename = resource_filename("text_analyze", "data/nltk/english.pickle")
tokenizer = nltk.data.load(filename)


def analyze_text(words, text, analyzers=[]):
    for analyzer in analyzers:
        for word in words:
            for sentence in text:
                analyzer.mark(word, sentence)

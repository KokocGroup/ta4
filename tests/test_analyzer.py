#! coding: utf-8
from text_analyze import analyze_text
from text_analyze.text import TextHtml
from text_analyze.sentence import Sentence
from text_analyze.analyzer import ExactAnalyzer, SubformsAnalyzer


def common_check(word, text, placeholders=[]):
    i = 0
    for num, ph in enumerate(text.sentences[0].place_holders):
        if num in placeholders:
            assert ph.markers[0].sentence.text == word.text
            assert ph.markers[0].position == i
            i += 1
        else:
            assert ph.markers == []


def test_exact_analyzer():
    test_table = [
        (u'пластиковые окна', u'купить пластиковые окна в москве', [1, 2]),
        (u'пластиковые окна', u'много хороших слов купить пластиковые окна', [4, 5]),
        (u'пластиковое окно', u'купить пластиковые окна в москве', []),
        (u'пластиковые окна', u'купить пластиковые великолепные окна в москве', []),
    ]
    for word, text, placeholders in test_table:
        word = Sentence(word)
        text = TextHtml(text)
        analyze_text([word], text, analyzers=[ExactAnalyzer()])
        common_check(word, text, placeholders)


def test_subform_analyzer():
    test_table = [
        (u'[пластиковое] [*] [окно]', u'купить пластиковые классные окна в москве', [1, 2, 3]),
        (u'[новогдняя] [ёлка]', u'купить новогднюю ёлку в москве недорого', [1, 2]),
        (u'[пластиковое] [*] [окно]', u'установка пластиковых окон', []),
        (u'[пластиковое] [*] [*] [окно]', u'пластиковые бронебойные анти-маскитные окна', [0, 1, 2, 3]),
    ]
    for word, text, placeholders in test_table:
        word = Sentence(word)
        text = TextHtml(text)
        analyze_text([word], text, analyzers=[SubformsAnalyzer()])
        common_check(word, text, placeholders)

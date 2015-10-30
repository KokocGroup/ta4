#! coding: utf-8
import pytest

from ta4 import find_similar_phrases, get_whole_markers
from ta4.text import TextHtml
from ta4.sentence import Sentence


@pytest.mark.parametrize("text, words, expected", [
    (
        u'Я хотел бы купить пластиковые окна в кредит недорого',
         [u'хотел', u'недорого', u'пластиковые окна'],
         [u"хотел * пластиковые", u"хотел * пластиковые окна", u"пластиковые окна * недорого", u"окна * недорого"]
    ),
    (
        u'Я хотел бы купить пластиковые окна в кредит недорого',
         [u'хотел', u'пластиковые окна'],
         [u"хотел * пластиковые", u"хотел * пластиковые окна"]
    ),
    (
        u'Я хотел бы купить пластиковые окна в кредит недорого',
         [u'пластиковые окна'],
         []
    ),
])
def test_find_similar_phrases(text, words, expected):
    text = TextHtml(text)
    words = map(Sentence, words)
    new_phrases = find_similar_phrases(words, text)
    assert len(new_phrases) == len(expected)
    assert set(new_phrases) == set(expected)


class Word(object):
    def __init__(self, word, markers):
        self.word = word
        self.markers = markers


@pytest.mark.parametrize("input, expected", [
    ([('A', True), ('A', False), ('A', True), ('A', True)], [[0, 0], [2, 3]]),
    ([('A', True), ('A', True), ('A', True), ('A', True)], [[0, 3]]),
    ([], []),
])
def test_get_whole_markers(input, expected):
    words = [Word(*item) for item in input]
    assert expected == get_whole_markers(words)

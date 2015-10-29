#! coding: utf-8
import pytest

from ta4 import find_similar_phrases, get_whole_markers
from ta4.text import TextHtml
from ta4.sentence import Sentence


def test_find_similar_phrases():
    text = TextHtml(u'Я хотел бы купить пластиковые окна в кредит недорого')
    words = map(Sentence, [
        u'хотел',
        u'недорого',
        u'пластиковые окна',
    ])
    new_phrases = find_similar_phrases(words, text)
    assert len(new_phrases) > 0
    assert set(new_phrases) == set([
        u"хотел * пластиковые",
        u"хотел * пластиковые окна",
        u"пластиковые окна * недорого",
        u"окна * недорого",
    ])


class Word(object):
    def __init__(self, word, markers):
        self.word = word
        self.markers = markers


@pytest.mark.parametrize("input,expected", [
    ([('A', True), ('A', False), ('A', True), ('A', True)], [[0, 0], [2, 3]]),
    ([('A', True), ('A', True), ('A', True), ('A', True)], [[0, 3]]),
])
def test_get_whole_markers(input, expected):
    words = [Word(*item) for item in input]
    assert expected == get_whole_markers(words)

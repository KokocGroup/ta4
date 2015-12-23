#! coding: utf-8
import pytest
from ta4 import absorptions, is_contains, Sentence


@pytest.mark.parametrize("input,result", [
    ([], []),
    (
        [(u"купить деревянный стол", 10),
         (u"купить * стол", 12)],
        [(u"купить деревянный стол", 10),
         (u"купить * стол", 2)],
    ),
    (
        [(u"купить длинный деревянный стол", 10),
         (u"купить * деревянный стол", 12),
         (u"купить * деревянный", 12)],
        [(u"купить длинный деревянный стол", 10),
         (u"купить * деревянный стол", 2),
         (u"купить * деревянный", 12)],
    ),
    (
        [(u"подъёмник мачтовый", 1),
         (u"подъёмник", 1),
         (u"мачтовый", 1)],

        [(u"подъёмник мачтовый", 1),
         (u"подъёмник", 0),
         (u"мачтовый", 0)]
    ),
    (
        [(u'[мачтовый]', 2),
         (u'[подъёмник]', 2),
         (u'[мачтовый] [подъёмник]', 2)],

        [(u'[мачтовый]', 0),
         (u'[подъёмник]', 0),
         (u'[мачтовый] [подъёмник]', 2)],
    )
])
def test_absorptions(input, result):
    assert set(absorptions(input)) == set(result)


@pytest.mark.parametrize("haystack, needle, result", [
    (u"купить стол", u"купить", True),
    (u"купить стол", u"стул", False),
    (u"купить стол", u"черепица", False),
    (u"купить деревянный стол в кредит", u"купить * стол", True),
])
def test_is_contains(haystack, needle, result):
    assert is_contains(Sentence(haystack), Sentence(needle)) == result

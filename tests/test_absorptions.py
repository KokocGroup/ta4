#! coding: utf-8
import pytest
from ta4 import absorptions, is_contains, Sentence


@pytest.mark.parametrize("input,result", [
    ([], []),
    (
        (
            (u'led телевизоры samsung', 2),
            (u'led * samsung', 3),
            (u'led телевизоры', 3),
            (u'led', 23)
        ),
        (
            (u'led телевизоры samsung', 2.0),
            (u'led * samsung', 1.0),
            (u'led телевизоры', 1.0),
            (u'led', 19.0)
        )
    ),
    (
        [
            (u"купить деревянный стол", 10.8),
            (u"купить * стол", 12.4),
            (u'купить', 40.8)
        ],
        [
            (u"купить деревянный стол", 10.8),
            (u"купить * стол", 1.6),
            (u'купить', 28.4)
        ],
    ),
    (
        [
            (u"купить длинный деревянный стол", 10),
            (u"купить * деревянный стол", 12.4),
            (u"купить * деревянный", 12)
        ],
        [
            (u"купить длинный деревянный стол", 10.0),
            (u"купить * деревянный стол", 2.4),
            (u"купить * деревянный", 12.0)
        ],
    ),
    (
        [
            (u"подъёмник мачтовый", 1),
            (u"подъёмник", 1),
            (u"мачтовый", 1)
        ],
        [
            (u"подъёмник мачтовый", 1.0),
            (u"подъёмник", 0.0),
            (u"мачтовый", 0.0)
        ]
    ),
    (
        [
            (u'[мачтовый]', 2),
            (u'[подъёмник]', 2),
            (u'[мачтовый] [подъёмник]', 2)
        ],
        [
            (u'[мачтовый]', 0.0),
            (u'[подъёмник]', 0.0),
            (u'[мачтовый] [подъёмник]', 2.0)
        ],
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

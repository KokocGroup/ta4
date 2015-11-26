#! coding: utf-8
import pytest
from ta4 import absorptions, is_contains, Sentence


@pytest.mark.parametrize("input,result", [
    ([], []),
    (
        [(u"купить стол", 10), (u"купить", 5), (u"стол", 3)],
        [(u"купить стол", 8), (u"купить", 5), (u"стол", 3)],
    ),
    (
        [(u"купить деревянный стол в кредит", 10),
         (u"купить деревянный", 5),
         (u"купить", 3)],
        [(u"купить деревянный стол в кредит", 8),
         (u"купить деревянный", 4),
         (u"купить", 3)],
    ),
    (
        [(u"купить деревянный стол", 10),
         (u"купить * стол", 12)],
        [(u"купить деревянный стол", 9),
         (u"купить * стол", 12)],
    ),
])
def test_absorptions(input, result):
    assert absorptions(input) == result


@pytest.mark.parametrize("haystack, needle, result", [
    (u"купить стол", u"купить", True),
    (u"купить стол", u"стул", False),
    (u"купить стол", u"черепица", False),
    (u"купить деревянный стол в кредит", u"купить * стол", True),
])
def test_is_contains(haystack, needle, result):
    assert is_contains(Sentence(haystack), Sentence(needle)) == result

#! coding: utf-8
from operator import attrgetter

import pytest

from ta4 import phrase_cmp
from ta4.sentence import Sentence
from ta4.placeholder import PlaceHolder, get_gram_infos


@pytest.mark.parametrize("text,length", [
    (u"Это обычный текст", 3),
    (u"Это обычный - текст", 4),
])
def test_creation(text, length):
    sentence = Sentence(text)
    assert sentence.text == text
    assert len(sentence) == length


def test_creation_subform_sentence():
    text = u'[пластиковые] [окна]'
    sentence = Sentence(text)
    assert text == sentence.text
    assert all([ph.is_subform_word for ph in sentence.place_holders]), True


@pytest.mark.parametrize("word,is_important,is_special", [
    (u'[*]', False, True),
    (u'*', False, True),
    (u'в', False, False),
    (u'машина', True, False),
    (u'для', False, False),
    (u'при', False, False),
    (u'окна', True, False),
    (u'пластиковые', True, False),
])
def test_lexeme_is_important(word, is_important, is_special):
    lexeme = PlaceHolder(word)
    assert lexeme.is_important == is_important
    assert lexeme.is_special == is_special


@pytest.mark.parametrize("word,counter", [
    (u'машина', 4),
    (u'окно', 2),
    (u'двигать', 1),
])
def test_get_gram_infos(word, counter):
    gram_info = get_gram_infos(word)
    assert len(gram_info) == counter


@pytest.mark.parametrize("one,another,result", [
    (u'купить пластиковое окно', u'пластиковое окно', 1),
    (u'купить окно', u'пластиковое окно', 0),
    (u'пластиковое окно', u'купить пластиковое окно', -1),

    (u'пластиковое окно', u'[купить] [пластиковое] [окно]', -1),
    (u'пластиковое окно', u'[купить] [*] [окно]', -1),
    (u'[запчасти] [грузового] [погрузчика]', u'[купить] [пластиковое] [окно]', 0),
    (u'[пластиковое] [окно]', u'[купить] [пластиковое] [окно]', -1),

    (u'[пластиковое] [*] [окно]', u'[купить] [пластиковое] [окно]', -1),
    (u'[купить] [пластиковое] [*] [окно]', u'[купить] [пластиковое] [окно]', 1),
    (u'[пластиковое] [*] [окно]', u'[запчасти] [*] [погрузчика]', 0),

    (u'окна', u'купить [*] окна', -1),
    (u'купить окна', u'купить [*] окна', -1),
    (u'купить окна', u'купить [*] окна в москве', -1),
    (u'купить [*] окна', u'купить [*] окна в москве', -1),
    (u'купить * шар', u'купить зеленый шар', -1),
])
def test_sorting_sentences(one, another, result):
    one, another = Sentence(one), Sentence(another)
    assert phrase_cmp(one, another) == result


def test_sorting_phrases():
    phrases = [
        u'[пластиковое] [*] [окно]',
        u'пластиковое окно',
        u'[купить] [пластиковое] [окно]',
        u'купить пластиковое окно',
    ]
    # отсортируем в порядке убыванию приоритета
    result = sorted(map(Sentence, phrases), cmp=phrase_cmp, reverse=True)
    result_texts = map(attrgetter('text'), result)
    assert result_texts[0] == phrases[3]
    assert result_texts[1] == phrases[2]
    assert result_texts[2] == phrases[0]
    assert result_texts[3] == phrases[1]

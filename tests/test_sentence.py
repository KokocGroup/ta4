#! coding: utf-8
from operator import attrgetter

from text_analyze import phrase_cmp
from text_analyze.sentence import Sentence
from text_analyze.lexeme import Lexeme


def test_creation():
    test_table = [
        (u"Это обычный текст", 3),
        (u"Это обычный - текст", 4),
    ]
    for text, length in test_table:
        sentence = Sentence(text)
        assert sentence.text == text
        assert len(sentence) == length


def test_creation_subform_sentence():
    text = u'[пластиковые] [окна]'
    sentence = Sentence(text)
    assert text == sentence.text
    assert all([ph.is_subform_word for ph in sentence.place_holders]), True


def test_lexeme_is_important():
    test_table = [
        (u'в', False),
        (u'машина', True),
        (u'для', False),
        (u'при', False),
        (u'окна', True),
        (u'пластиковые', True),
    ]
    for word, is_important in test_table:
        assert Lexeme(word).is_important == is_important


def test_sorting_sentences():
    test_table = [
        (u'купить пластиковое окно', u'пластиковое окно', 1),
        (u'купить окно', u'пластиковое окно', 0),
        (u'пластиковое окно', u'купить пластиковое окно', -1),

        (u'пластиковое окно', u'[купить] [пластиковое] [окно]', 1),
        (u'пластиковое окно', u'[купить] [*] [окно]', 1),
        (u'[запчасти] [грузового] [погрузчика]', u'[купить] [пластиковое] [окно]', 0),
        (u'[пластиковое] [окно]', u'[купить] [пластиковое] [окно]', -1),

        (u'[пластиковое] [*] [окно]', u'[купить] [пластиковое] [окно]', -1),
        (u'[купить] [пластиковое] [*] [окно]', u'[купить] [пластиковое] [окно]', 1),
        (u'[пластиковое] [*] [окно]', u'[запчасти] [*] [погрузчика]', 0),
    ]

    for one, another, result in test_table:
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
    assert result_texts[1] == phrases[1]
    assert result_texts[2] == phrases[2]
    assert result_texts[3] == phrases[0]

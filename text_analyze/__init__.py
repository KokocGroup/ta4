#! coding: utf-8
from pkg_resources import resource_filename

import nltk
import pymorphy2

morph = pymorphy2.MorphAnalyzer()
filename = resource_filename("text_analyze", "data/nltk/english.pickle")
tokenizer = nltk.data.load(filename)


def mark_with_words(words, text, analyzers=[]):
    u"""
    Находит в тексте вхождения слов, при помощи анализаторов.
    Видоизменяет плейсхолдеры текста, добавляя маркеры фраз под которые подходит плейсхолдер.

    :param words: list text_analyze.sentence.Sentence
    :param text: list text_analyze.text.TextHtml
    :param analyzers: list text_analyze.analyzer.IAnalyzer
    """
    for analyzer in analyzers:
        for word in words:
            for sentence in text:
                analyzer.mark(word, sentence)


def find_words(words, text):
    u"""
    Из размеченного текста(функцией mark_with_words), выбирает вхождения слов,
    и формирует список какая фраза сколько раз вошло в текст, согласно приоритетам:
     - точное вхождение, приоритетнее вхождения по словоформам("пластиковые окна" > "[купить] [пластиковое] [окно]")
     - вхождение с большим числом слов, приоритетнее ("купить пластивые окна" > "пластиковое окно")
     - при сравнении вхождений по словоформам при равенстве числа слов, приоритетнее то,
       в котором меньше звёздочек ("[купить] [пластиковое] [окно]" > "[купить] [*] [окно]")
    """
    for word in sorted(words, cmp=phrase_cmp):
        for sentence in text:
            pass


def phrase_cmp(one, another):
    """
    Функция сравнения, для сортировки фраз по порядку их приоритета
    :param one: text_analyze.sentence.Sentence
    :param another: text_analyze.sentence.Sentence
    """
    # точное вхождение приоритетнее словоформ
    subform_cmp = cmp(one.is_exact_task, another.is_exact_task)
    if subform_cmp != 0:
        return subform_cmp
    # фраза с большим числом слов - приоритетнее
    len_cmp = cmp(len(one), len(another))
    if len_cmp != 0:
        return len_cmp

    # для словоформ с равным числом слов, приоритетное то, где меньше звёздочек
    if not one.is_exact_task and not another.is_exact_task:
        return cmp(one.count(u'[*]'), another.count(u'[*]')) * -1
    return len_cmp

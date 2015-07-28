#! coding: utf-8
from collections import defaultdict, OrderedDict
from pkg_resources import resource_filename

import nltk
import pymorphy2

from .analyzer import ExactAnalyzer, SubformsAnalyzer


morph = pymorphy2.MorphAnalyzer()
filename = resource_filename("ta4", "data/nltk/english.pickle")
tokenizer = nltk.data.load(filename)


def mark_with_words(words, text, analyzers={}):
    u"""
    Находит в тексте вхождения слов, при помощи анализаторов.
    Видоизменяет плейсхолдеры текста, добавляя маркеры фраз под которые подходит плейсхолдер.

    :param words: list text_analyze.sentence.Sentence
    :param text: list text_analyze.text.TextHtml
    :param analyzers: list text_analyze.analyzer.IAnalyzer
    """

    analyzers = analyzers or {
        True: ExactAnalyzer(),
        False: SubformsAnalyzer(),
    }

    for word in words:
        for sentence in text:
            analyzer = analyzers[word.is_exact_task]
            analyzer.mark(word, sentence)


def find_words(words, text):
    u"""
    Из размеченного текста(функцией mark_with_words), выбирает вхождения слов,
    и формирует список какая фраза сколько раз вошло в текст, согласно приоритетам:
     - точное вхождение, приоритетнее вхождения по словоформам("пластиковые окна" > "[купить] [пластиковое] [окно]")
     - вхождение с большим числом слов, приоритетнее ("купить пластивые окна" > "пластиковое окно")
     - при сравнении вхождений по словоформам при равенстве числа слов, приоритетнее то,
       в котором меньше звёздочек ("[купить] [пластиковое] [окно]" > "[купить] [*] [окно]")

    В результате получим подсчёт количества вхождений words в text, и дополненное задание
    """
    counter = {w.text: 0 for w in words}
    new_tasks = defaultdict(int)
    for sentence in text:
        markers = OrderedDict()
        for ph in sentence.place_holders:
            for marker in ph.markers:
                if marker.sentence not in markers:
                    markers[marker.sentence] = {'min': ph.position}
                else:
                    markers[marker.sentence]['max'] = ph.position

        markers = markers.items()
        N = len(markers)
        i = 0
        while i < N:
            sentence, marker = markers[i]
            if i < N-1:
                next_sentence, next_marker = markers[i+1]
                # если маркеры отметили один и тот же участок предложения,
                # побеждает сильнейший
                if marker == next_marker:
                    winner = sorted([sentence, next_sentence], cmp=phrase_cmp, reverse=True)[0]
                    counter[winner.text] += 1
                elif next_marker['min'] > marker['max']:
                    # пересечения нет
                    counter[sentence.text] += 1
                else:
                    if next_marker['max'] > marker['max']:
                        # пересечение
                        counter[sentence.text] += 1
                        counter[next_sentence.text] += 1
                        new_phrase = []
                        for ph in sentence.place_holders[next_marker['min']:marker['max']+1]:
                            new_phrase.append(ph.origin_word)
                        new_phrase = u' '.join(new_phrase)
                        new_tasks[new_phrase] += 1
                    else:
                        # поглощение - вовсе пропускаем следующий маркет
                        counter[sentence.text] += 1
                i += 2
                continue
            else:
                counter[sentence.text] += 1
            i += 1

    return counter, dict(new_tasks)


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

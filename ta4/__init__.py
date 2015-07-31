#! coding: utf-8
from operator import itemgetter
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
    """
    # Ключом будет являться, является ли задание - заданием на поиск точного вхождения
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
                    markers[marker.sentence] = {'min': ph.position, 'max': ph.position}
                else:
                    markers[marker.sentence]['max'] = ph.position
        # купить пластиковые окна: {min: 2, max: 4}
        # пластиковые окна в москве: {min: 3, max: 6}

        markers = markers.items()
        # группируем маркеры по пересечению
        # в итоге получим кластера, которые хоть как то пересекаются
        for markers_chunk in group_markers(markers):
            if len(markers_chunk) == 1:
                # пересечений по маркерам нет
                marker_sentence, _ = markers_chunk[0]
                counter[marker_sentence.text] += 1
            else:
                # подсчитываем вхождения и добавляем попарное пересечение в задание
                length = len(markers_chunk) - 1
                for i, (marker_sentence, marker) in enumerate(markers_chunk):
                    counter[marker_sentence.text] += 1
                    if i < length:
                        _, next_marker = markers_chunk[i+1]
                        text = get_intersection(marker, next_marker, sentence)
                        new_tasks[text] += 1

    return counter, dict(new_tasks)


def group_markers(markers):
    result = []
    length = len(markers) - 1
    for i, (_, marker) in enumerate(markers):
        result.append(markers[i])
        if i < length:
            _, next_marker = markers[i+1]
            if next_marker['min'] > marker['max']:
                # сортируем по приоритету
                result = sorted(result, cmp=phrase_cmp, key=itemgetter(0), reverse=True)
                # отфильтровываем поглащённые
                result = merge_filter(result)
                if result:
                    yield result
                result = []
    result = sorted(result, cmp=phrase_cmp, key=itemgetter(0), reverse=True)
    result = merge_filter(result)
    if result:
        yield result


def merge_filter(markers):
    """
    Фильтрует маркеры на предмет полного поглощения, так как markers отсортированы по приоритету,
    функция выкинет маркеры, которые полностью поглощаются более приоритетными фразами
    """
    result = []
    for i, (sentence, marker) in enumerate(markers):
        # смотрим на предыдущие маркеры, входит ли в них i-ый
        for _, bigger_marker in result:
            if bigger_marker['min'] <= marker['min'] <= bigger_marker['max'] \
               and bigger_marker['min'] <= marker['max'] <= bigger_marker['max']:
                break
        else:
            result.append((sentence, marker))
    return result


def get_intersection(marker, next_marker, sentence):
    """
    Возвращает текст из пересечения маркеров
    """
    #  пересечение вида ------
    #                       ------
    if marker['min'] <= next_marker['min'] <= marker['max'] and next_marker['max'] > marker['max']:
        i, j = next_marker['min'], marker['max']
    #  пересечение вида ---
    #                 --------
    elif next_marker['min'] < marker['max'] and next_marker['max'] > marker['max']:
        i, j = marker['min'], marker['max']
    #  пересечение вида ---------
    #                     ----
    elif marker['min'] < next_marker['min'] < marker['max'] and marker['min'] < next_marker['max'] < marker['max']:
        i, j = next_marker['min'], next_marker['max']
    #  пересечение вида --------
    #               --------
    else:
        i, j = marker['min'], next_marker['max']
    phrase = []
    for ph in sentence.place_holders:
        if i <= ph.position <= j:
            phrase.append(ph.origin_word)

    return u' '.join(phrase)


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

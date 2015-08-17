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


SPECIAL_WORDS = '[*]', '*'


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
    number = 1  # скозная нумерация маркеров
    for word in words:
        for sentence in text:
            analyzer = analyzers[word.is_exact_task]
            number = analyzer.mark(word, sentence, number)


def find_words(words, text):
    u"""
    Из размеченного текста(функцией mark_with_words), выбирает вхождения слов,
    и формирует список какая фраза сколько раз вошло в текст, согласно приоритетам:
     - Фраза с большим числом точных вхождений приоритетнее("купить пластиковые окна" > "купить [*] окно",
        "купить зеленый шар" > "купить * шар")
     - вхождение с большим числом слов, приоритетнее ("купить пластивые окна" > "пластиковое окно")
     - при сравнении вхождений по словоформам при равенстве числа слов, приоритетнее то,
       в котором меньше звёздочек ("[купить] [пластиковое] [окно]" > "[купить] [*] [окно]")

    В результате получим подсчёт количества вхождений words в text, и дополненное задание
    """
    counter = {w.text: 0 for w in words}
    new_tasks = defaultdict(int)
    for sentence in text:
        markers = get_markers(sentence)
        # группируем маркеры по пересечению
        # в итоге получим кластера, которые хоть как то пересекаются
        for markers_chunk in group_markers(markers):
            if len(markers_chunk) == 1:
                # пересечений по маркерам нет
                marker_sentence, marker = markers_chunk[0]
                counter[marker_sentence.text] += 1
                activate_marker(marker_sentence, marker, sentence)
            else:
                # подсчитываем вхождения и добавляем попарное пересечение в задание
                length = len(markers_chunk) - 1
                for i, (marker_sentence, marker) in enumerate(markers_chunk):
                    counter[marker_sentence.text] += 1
                    activate_marker(marker_sentence, marker, sentence)
                    if i < length:
                        _, next_marker = markers_chunk[i+1]
                        text = get_intersection(marker, next_marker, sentence)
                        new_tasks[text] += 1

    return counter, dict(new_tasks)


def activate_marker(marker_sentence, marker, sentence):
    for placeholder in sentence.place_holders:
        if marker['min'] <= placeholder.position <= marker['max']:
            for m in placeholder.markers:
                if m.sentence == marker_sentence:
                    m.is_active = True


def get_markers(sentence):
    """
    Для предложения вернёт все маркеры, с диапазоноп позиций

    (u'купить пластиковые окна', {min: 2, max: 4})
    (u'купить пластиковые окна', {min: 9, max: 11})
    (u'пластиковые окна в москве', {min: 3, max: 6})
    """
    markers = OrderedDict()
    marker_id_to_sentence = {}
    for ph in sentence.place_holders:
        for marker in ph.markers:
            marker_id_to_sentence[marker.id] = marker.sentence
            if marker.id not in markers:
                markers[marker.id] = {'min': ph.position, 'max': ph.position}
            else:
                markers[marker.id]['max'] = ph.position
    result = [(marker_id_to_sentence[pk], positions) for pk, positions in markers.items()]
    return result


def group_markers(markers):
    result = []
    length = len(markers) - 1
    max_pos = 0
    for i, (_, marker) in enumerate(markers):
        result.append(markers[i])
        if max_pos < marker['max']:
            max_pos = marker['max']
        if i < length:
            _, next_marker = markers[i+1]
            # Проверяем, не началась ли другая группа маркеров
            if next_marker['min'] > max_pos:
                # сортируем по приоритету
                result = sorted(result, cmp=phrase_cmp, key=itemgetter(0), reverse=True)
                # отфильтровываем поглащённые
                result = merge_filter(result)
                if result:
                    yield result
                max_pos = next_marker['max']
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
    # фраза с большим числом точных вхождений, приоритетнее
    len_exact_cmp = cmp(one.exact_count, another.exact_count)
    if len_exact_cmp != 0:
        return len_exact_cmp
    # фраза с большим числом слов - приоритетнее
    len_cmp = cmp(len(one), len(another))
    if len_cmp != 0:
        return len_cmp

    # для словоформ с равным числом слов, приоритетное то, где меньше звёздочек
    for spec_word in SPECIAL_WORDS:
        res = cmp(one.count(spec_word), another.count(spec_word)) * -1
        if res != 0:
            return res
    return len_cmp

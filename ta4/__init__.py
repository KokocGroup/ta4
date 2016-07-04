#! coding: utf-8
from operator import itemgetter
from collections import defaultdict, OrderedDict
from pkg_resources import resource_filename
import math
import nltk
import pymorphy2

from .analyzer import ExactAnalyzer, SubformsAnalyzer
from .sentence import Sentence


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
    for word in set(words):
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
        for (markers_chunk, phantoms) in group_markers(markers, sentence):
            if len(markers_chunk) == 1:
                # пересечений по маркерам нет
                marker_sentence, marker = markers_chunk[0]
                counter[marker_sentence.text] += 1
                activate_marker(marker_sentence, marker, sentence)
            else:
                for i, (marker_sentence, marker) in enumerate(markers_chunk):
                    counter[marker_sentence.text] += 1
                    activate_marker(marker_sentence, marker, sentence)
                for phantom in phantoms:
                    new_tasks[phantom.lower()] += 1

    return counter, dict(new_tasks)


def get_marked_words(text):
    u"""
    Из размеченного текста вернёт слова которые в нём размечены и количество вхождений
    """
    mapping = defaultdict(int)
    for sentence in text:
        for keyword, _ in get_markers(sentence):
            mapping[keyword.text] += 1
    return dict(mapping)


def find_similar_phrases(phrases, text):
    u"""
    Находит похожие фразы. Если в предложении мы встретили какое нибудь слово из фраз,
    то мы нарезаем это предложение на фразы. Максимальный промежуток между вхождениями
    одно значимое слово
    """
    words = set([Sentence(word.word) for phrase in phrases for word in phrase])
    new_phrases = []
    mark_with_words(words, text)
    for sentence in text:
        # делаем обратный маппинг - позиция в предложении на диапазон его маркера
        # TODO маркера не подойдут - ведь возможно пересечение!!
        words = [ph for ph in sentence if ph.is_important]

        mapping = {}
        for min_index, max_index in get_whole_markers(words):
            for i in xrange(min_index, max_index+1):
                mapping[i] = dict(min=min_index, max=max_index)

        # находим слово без маркеров, но что бы слева и справа стояли слова с маркерами
        for i, word in enumerate(words[1:-1], 1):
            if not word.markers and words[i-1].markers and words[i+1].markers:
                left = mapping[i-1]['min']
                right = mapping[i+1]['max']
                # left_marker(left, i-1), *, right_marker(i+1, right)
                for k in range(left, i):
                    for l in range(i+1, right+1):
                        phrase = []
                        for x in range(k, l+1):
                            if x != i:
                                phrase.append(words[x].word)
                            else:
                                phrase.append(u'*')
                        new_phrases.append(u" ".join(phrase))
    return map(unicode.lower, new_phrases)


def get_whole_markers(words):
    """
    Находим маркерные пятна - непрерывные куски промаркированных слов
    """
    if not words:
        return []
    in_group = bool(words[0].markers)
    groups = []
    current_group = None
    if in_group:
        current_group = [0, 0]

    for i, word in enumerate(words):
        is_marker = bool(word.markers)
        if is_marker and not current_group:
            current_group = [i, i]

        if not is_marker and in_group:
            groups.append(current_group)
            current_group = None
        else:
            if in_group and is_marker:
                current_group[1] = i

        in_group = is_marker
    else:
        if current_group:
            groups.append(current_group)

    return groups


def absorptions(phrases):
    u"""
    Поглощения фраз
    на вход список фраз/вхождений - [("one phrase", 10), ("phrase", 2)]
    """
    phrases = [(Sentence(phrase), float(count)) for phrase, count in phrases]
    phrases = OrderedDict(sorted(phrases, cmp=phrase_cmp, key=itemgetter(0), reverse=True))

    for phrase in phrases:
        for candidate, candidate_count in phrases.items():
            if phrase == candidate:
                continue
            if phrase.is_special and len(phrase) != len(candidate):
                continue
            if is_contains(candidate, phrase) and candidate_count > 0:
                phrases[phrase] = max((phrases[phrase] - candidate_count, 0))
    return [(phrase.text, float(str(count))) for phrase, count in phrases.iteritems()]


def is_contains(haystack, needle):
    return bool(SubformsAnalyzer().mark(needle, haystack, 0, should_mark=False))


def activate_marker(marker_sentence, marker, sentence):
    inactive = []
    for placeholder in sentence.place_holders:
        if marker['min'] <= placeholder.position <= marker['max']:
            for m in placeholder.markers:
                if m.sentence == marker_sentence:
                    m.is_active = True
                else:
                    inactive.append(m)

    # маркируем неактивные маркеры предложением которое должно
    for placeholder in sentence.place_holders:
        if marker['min'] <= placeholder.position <= marker['max']:
            for m in placeholder.markers:
                if m.sentence == marker_sentence:
                    for inactive_marker in inactive:
                        m.target_sentence.add(inactive_marker.simple_hash())


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


def get_marker_sentences(text):
    result = {}
    for sentence in text:
        for ph in sentence.place_holders:
            for marker in ph.markers:
                result.setdefault(marker.sentence.text, {}).setdefault(marker.id, []).append(ph.word)
    return {keyword.lower(): map(lambda x: u" ".join(x).lower(), data.values()) for keyword, data in result.iteritems()}


def group_markers(markers, sentence):
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
                result, phantoms = merge_filter(result, sentence)
                if result:
                    yield result, phantoms
                max_pos = next_marker['max']
                result = []
    result = sorted(result, cmp=phrase_cmp, key=itemgetter(0), reverse=True)
    result, phantoms = merge_filter(result, sentence)
    if result:
        yield result, phantoms


def merge_filter(markers, original_sentence):
    """
    Фильтрует маркеры на предмет полного поглощения, так как markers отсортированы по приоритету,
    функция выкинет маркеры, которые полностью поглощаются более приоритетными фразами
    """
    result = []
    phantoms = []
    if not markers:
        return result, phantoms

    # Для группы маркеров создаём индексы доступных плейсхолдеров
    minimum = min(map(lambda x: x[1]['min'], markers))
    maximum = max(map(lambda x: x[1]['max'], markers))

    indexes = range(minimum, maximum+1)
    for (sentence, marker) in markers:
        marker_borders = range(marker['min'], marker['max']+1)
        free_elements = map(lambda x: x in indexes, marker_borders)
        # если удалось наложить фразу на плейсхолдеры без конфликтов
        if all(free_elements):
            result.append((sentence, marker))
        elif any(free_elements):
            # удалось наложить частично
            length = len(sentence.place_holders)
            little_phantoms = []
            for i, value in enumerate(free_elements):
                if not value:
                    if i < length:
                        little_phantoms.append(i)
                elif little_phantoms:
                    phantoms.append(_get_phantom(little_phantoms, original_sentence, offset=marker['min']))
                    little_phantoms = []
            if little_phantoms:
                phantoms.append(_get_phantom(little_phantoms, original_sentence, offset=marker['min']))
            result.append((sentence, marker))

        for i in marker_borders:
            if i in indexes:
                indexes.remove(i)

    return result, phantoms


def _get_phantom(indexes, sentence, offset):
    phantom = []
    indexes = map(lambda x: x+offset, indexes)
    for ph in sentence:
        if ph.position in indexes:
            phantom.append(ph.word)
    return ' '.join(phantom)


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
    # фраза с большим числом слов - приоритетнее
    len_cmp = cmp(len(one), len(another))
    if len_cmp != 0:
        return len_cmp

    # фраза с большим числом точных вхождений, приоритетнее
    len_exact_cmp = cmp(one.exact_count, another.exact_count)
    if len_exact_cmp != 0:
        return len_exact_cmp

    # для словоформ с равным числом слов, приоритетное то, где меньше звёздочек
    for spec_word in SPECIAL_WORDS:
        res = cmp(one.count(spec_word), another.count(spec_word)) * -1
        if res != 0:
            return res
    return len_cmp

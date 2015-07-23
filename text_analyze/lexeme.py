#!/usr/bin/env python
# -*-coding: utf-8 -*-
import re
from collections import defaultdict
from operator import attrgetter

from . import morph
from gram_info import GramInfo


gram_infos_cache = defaultdict(list)
word_regexp = re.compile(u"^\w+-?(\w+-)*\w+$", re.DOTALL | re.IGNORECASE | re.MULTILINE | re.VERBOSE | re.UNICODE)
clean_word_regexp = re.compile(ur'^[^\w]*([-\w]+)[^\w]*$', re.U | re.I)


def get_gram_infos(word):
    global gram_infos_cache

    searched = word_regexp.search(word)
    if not searched:
        return []

    word = word.upper()
    if word not in gram_infos_cache:
        gram_infos = morph.get_graminfo(word)
        if not gram_infos:
            gram_infos = [{'lemma': word, 'norm': word, 'speech': 'C', 'class': 'C'}]

        for gi in gram_infos:
            # это хак по слову "ДЛЯ". get_graminfo возвращает для него две нормальных формы ДЛЯ и ДЛИТЬ что неверно.
            # Должно быть только ДЛЯ.
            if (word == u'ДЛЯ' and gi['norm'] != u'ДЛЯ') or (word == u'ПРИ' and gi['norm'] != u'ПРИ'):
                continue
            if (word == u'ПЕРЕД'):
                gi['class'] = u'ПРЕДЛ'
            gram_infos_cache[word].append(GramInfo(gi))

    return gram_infos_cache[word]


class Lexeme(object):
    u"""Класс описывает лексемму.

    Под **лексеммой** понимаем абстрактную единицу текста (слово, разделитель слов, знаки препинания и т.п.).

    Параметры конструктора:

    * **word** - слово в :py:class:`unicode`
    """

    __slots__ = ('word', 'origin_word', 'is_word', 'gram_infos')

    SPECIAL_WORD = '] [*] ['

    def __init__(self, word):
        clear_word = clean_word_regexp.sub(ur'\1', word)
        self.word = clear_word.upper()
        self.origin_word = clear_word
        self.gram_infos = get_gram_infos(clear_word)
        self.is_word = bool(self.gram_infos) or word == self.SPECIAL_WORD

    def get_gram_info(self, key):
        if self.gram_infos:
            return map(attrgetter(key), self.gram_infos)
        return self.word

    def normalize(self):
        u"""Нормализация лексеммы - инфинитив"""
        return self.get_gram_info('infinitive')

    def full_normalize(self):
        return map(attrgetter('infinitive'), filter(bool, self.gram_infos))

    def lemmatize(self):
        u"""Лемматизация лексеммы - основа слова"""
        return self.get_gram_info('lemma')

    def __eq__(self, other):
        u"""Сравнение двух лексемм на равество"""
        return self.word == other.word

    def like_to(self, other):
        u"""Сравнение лексемм на похожесть"""
        for self_norm in self.normalize():
            for other_norm in other.normalize():
                if self_norm and other_norm:
                    if self_norm == other_norm:
                        return True
                    else:
                        for lemm_1 in self.lemmatize():
                            for lemm_2 in other.lemmatize():
                                if lemm_1 and lemm_2 and lemm_1 == lemm_2:
                                    return True
        return False

    def get_all_normal_phorms(self):
        return set(map(attrgetter('infinitive'), self.gram_infos))

#!/usr/bin/env python
# -*-coding: utf-8 -*-
import re
from operator import attrgetter

from . import morph


clean_word_regexp = re.compile(ur'^[^\w]*([-\w]+)[^\w]*$', re.U | re.I)


PARTS_OF_SPEECH = set([
    u'ADJF',  # имя прилагательное (полное)
    u'ADJS',  # имя прилагательное (краткое)
    u'ADVB',  # наречие
    u'COMP',  # компаратив
    u'CONJ',  # союз
    u'GRND',  # деепричастие
    u'INFN',  # глагол (инфинитив)
    u'INTJ',  # междометие
    u'NOUN',  # имя существительное
    u'NPRO',  # местоимение-существительное
    u'NUMR',  # числительное
    u'PRCL',  # частица
    u'PRED',  # предикатив
    u'PREP',  # предлог
    u'PRTF',  # причастие (полное)
    u'PRTS',  # причастие (краткое)
    u'VERB',  # глагол (личная форма)
])

IMPORTANT_PARTS_OF_SPEECH = PARTS_OF_SPEECH - set(['NPRO', 'PRED', 'PREP', 'CONJ', 'INTJ', 'PRCL'])


class GramInfo(object):
    __slots__ = ('normal_form', 'part_of_speech')

    def __init__(self, normal_form, part_of_speech):
        self.normal_form = normal_form
        self.part_of_speech = part_of_speech

    def __repr__(self):
        return u"<inf: %s>" % self.normal_form

    @property
    def is_important_pos(self):
        return self.part_of_speech in IMPORTANT_PARTS_OF_SPEECH


def get_gram_infos(word):
    results = morph.parse(word)
    if not results:
        return [GramInfo(word)]
    return [GramInfo(r.normal_form, r.tag.POS) for r in results]
    return map(GramInfo, map(attrgetter('normal_form'), results))


class Lexeme(object):
    __slots__ = ('word', 'origin_word', 'gram_infos')

    SPECIAL_WORD = '[*]'

    def __init__(self, word):
        clear_word = clean_word_regexp.sub(ur'\1', word)
        self.word = clear_word.upper()
        self.origin_word = clear_word.upper()
        self.gram_infos = get_gram_infos(clear_word)

    @property
    def is_special(self):
        return self.origin_word == self.SPECIAL_WORD

    @property
    def is_important(self):
        u"""Не важная часть речи, например предлоги или частицы, не учавствуют в сравнениях"""
        return all(map(attrgetter('is_important_pos'), self.gram_infos))

    def get_all_normal_phorms(self):
        return set(map(attrgetter('normal_form'), self.gram_infos))
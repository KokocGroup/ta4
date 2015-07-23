#!/usr/bin/env python
# -*-coding: utf-8 -*-
import re
from operator import attrgetter

from . import morph


word_regexp = re.compile(u"^\w+-?(\w+-)*\w+$", re.DOTALL | re.IGNORECASE | re.MULTILINE | re.VERBOSE | re.UNICODE)
clean_word_regexp = re.compile(ur'^[^\w]*([-\w]+)[^\w]*$', re.U | re.I)


class GramInfo(object):
    __slots__ = ('normal_form', )

    def __init__(self, normal_form):
        self.normal_form = normal_form

    def __repr__(self):
        return u"<inf: %s>" % self.normal_form


def get_gram_infos(word):
    if not word_regexp.search(word):
        return []

    results = morph.parse(word)
    if not results:
        return [GramInfo(word)]
    return map(GramInfo, map(attrgetter('normal_form'), results))


class Lexeme(object):
    __slots__ = ('word', 'origin_word', 'is_word', 'gram_infos')

    SPECIAL_WORD = '[*]'

    def __init__(self, word):
        clear_word = clean_word_regexp.sub(ur'\1', word)
        self.word = clear_word.upper()
        self.origin_word = clear_word
        self.gram_infos = get_gram_infos(clear_word)
        self.is_word = bool(self.gram_infos) or word == self.SPECIAL_WORD

    @property
    def is_special(self):
        return self.origin_word == self.SPECIAL_WORD

    def get_all_normal_phorms(self):
        return set(map(attrgetter('normal_form'), self.gram_infos))

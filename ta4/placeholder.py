# -*-coding: utf-8 -*-
import hashlib
import re
from operator import attrgetter

from . import morph, SPECIAL_WORDS


clean_word_regexp = re.compile(ur'^[^\w]*([-\w]+)[^\w]*$', re.U | re.I)

CACHE = {}

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


class Marker(object):
    __slots__ = ('id', 'sentence', 'position', 'is_active', 'target_sentence', )

    def __init__(self, sentence, position, marker_id):
        """
        marker_id - признак позволяющий найти
        """
        self.id = marker_id
        self.sentence = sentence
        self.position = position
        self.is_active = False
        self.target_sentence = set()

    @property
    def hash(self):
        marker_hash = hashlib.md5(self.sentence.text.encode('utf-8')).hexdigest()
        if self.is_active:
            return marker_hash
        return "inactive-%s" % marker_hash

    def simple_hash(self):
        return hashlib.md5(self.sentence.text.encode('utf-8')).hexdigest()


class PlaceHolder(object):
    __slots__ = ('word', 'origin_word', 'gram_infos', 'markers', 'position', 'is_subform_word')

    def __init__(self, word, position=0):
        clear_word = clean_word_regexp.sub(ur'\1', word)
        self.word = clear_word.upper()
        self.origin_word = clear_word.upper()
        self.gram_infos = get_gram_infos(clear_word.lower())
        self.position = position
        self.markers = []
        # этот плейсхолдер - словоформа
        self.is_subform_word = word.startswith('[') and word.endswith(']')

    def add_marker(self, position, word, marker_id):
        marker = Marker(word, position, marker_id)
        self.markers.append(marker)

    def clean(self):
        self.markers = []

    @property
    def is_special(self):
        return self.origin_word in SPECIAL_WORDS

    @property
    def is_word(self):
        return self.origin_word not in {u'–'}

    @property
    def is_important(self):
        u"""Не важная часть речи, например предлоги или частицы, не учавствуют в сравнениях"""
        if self.is_special:
            return False
        return all(map(attrgetter('is_important_pos'), self.gram_infos))

    def get_all_normal_phorms(self):
        return set(map(attrgetter('normal_form'), self.gram_infos))

    def __repr__(self):
        return self.word.encode('utf-8')


class GramInfo(object):
    __slots__ = ('normal_form', 'part_of_speech')

    def __init__(self, normal_form, part_of_speech):
        self.normal_form = normal_form
        self.part_of_speech = part_of_speech or u'NOUN'

    @property
    def is_important_pos(self):
        return self.part_of_speech in IMPORTANT_PARTS_OF_SPEECH


def get_gram_infos(word):
    # пока так неэлегантно, но увы
    if word in CACHE:
        return CACHE[word]
    if word.startswith(u'лучш'):
        return [GramInfo(u'лучший', u'ADJF')]
    elif word == u'дети':
        return [GramInfo(u'дети', u'NOUN')]

    results = morph.parse(word)
    results = CACHE[word] = [GramInfo(r.normal_form, r.tag.POS) for r in results]
    return results

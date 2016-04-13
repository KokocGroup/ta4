# -*-coding: utf-8 -*-
import hashlib
import re
from operator import attrgetter

from . import morph, SPECIAL_WORDS


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


class PlaceholderCreator(object):
    def __init__(self):
        self.cache = {}

    def get_gram_infos(self, word):
        # пока так неэлегантно, но увы
        if word in self.cache:
            return self.cache[word]
        if word.lower().startswith(u'лучш'):
            return [GramInfo(u'лучший', u'ADJF')]
        elif word.lower() == u'дети':
            return [GramInfo(u'дети', u'NOUN')]
        elif word.lower() == u'oled':
            return [GramInfo(u'oled', 'PRTS')]
        elif word.lower() == u'м':
            return [GramInfo(u'метр', 'NOUN')]

        results = morph.parse(word)
        self.cache[word] = [GramInfo(r.normal_form, r.tag.POS) for r in results]
        return self.cache[word]

    def create(self, word, position=0):
        clear_word = clean_word_regexp.sub(ur'\1', word)
        gram_infos = self.get_gram_infos(clear_word.lower())
        is_subform = word.startswith('[') and word.endswith(']')
        return PlaceHolder(clear_word, position, gram_infos, is_subform)


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
    __slots__ = ('word', 'gram_infos', 'markers', 'position', 'is_subform_word', '_lexemes', 'is_word', 'is_special', 'is_important')

    def __init__(self, word, position, gram_infos, is_subform):
        self.word = word.upper()
        self.position = position
        self.gram_infos = gram_infos
        self.markers = []
        self.is_subform_word = is_subform
        self._lexemes = None
        self.is_word = self.word not in {u'–'}
        self.is_special = self.word in SPECIAL_WORDS
        if self.is_special:
            self.is_important = False
        else:
            self.is_important = all(map(attrgetter('is_important_pos'), self.gram_infos))

    def add_marker(self, word, position, marker_id):
        marker = Marker(word, position, marker_id)
        self.markers.append(marker)

    def clean(self):
        self.markers = []

    def get_all_normal_phorms(self):
        return set(map(attrgetter('normal_form'), self.gram_infos))

    def __repr__(self):
        return self.word.encode('utf-8')

    @property
    def lexemes(self):
        if not self._lexemes:
            words = morph.parse(self.word)
            self._lexemes = list(set(l.word for w in words for l in w.lexeme))
        return self._lexemes


class GramInfo(object):
    __slots__ = ('normal_form', 'part_of_speech')

    def __init__(self, normal_form, part_of_speech):
        self.normal_form = normal_form
        self.part_of_speech = part_of_speech or u'NOUN'

    @property
    def is_important_pos(self):
        return self.part_of_speech in IMPORTANT_PARTS_OF_SPEECH

# -*-coding: utf-8 -*-
import hashlib

from lexeme import Lexeme


class Marker(object):
    def __init__(self, sentence, position):
        self.sentence = sentence
        self.position = position

    @property
    def hash(self):
        return hashlib.md5(self.sentence.text.encode('utf-8')).hexdigest()


class PlaceHolder(Lexeme):
    def __init__(self, word, position):
        super(PlaceHolder, self).__init__(word)
        self.position = position
        self.markers = []
        # этот плейсхолдер - словоформа
        self.is_subform_word = word.startswith('[') and word.endswith(']')

    def add_marker(self, position, word):
        marker = Marker(word, position)
        self.markers.append(marker)

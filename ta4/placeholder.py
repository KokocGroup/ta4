# -*-coding: utf-8 -*-
import hashlib

from lexeme import Lexeme


class Marker(object):
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


class PlaceHolder(Lexeme):
    def __init__(self, word, position):
        super(PlaceHolder, self).__init__(word)
        self.position = position
        self.markers = []
        # этот плейсхолдер - словоформа
        self.is_subform_word = word.startswith('[') and word.endswith(']')

    def add_marker(self, position, word, marker_id):
        marker = Marker(word, position, marker_id)
        self.markers.append(marker)

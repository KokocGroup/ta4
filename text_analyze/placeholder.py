# -*-coding: utf-8 -*-
from lexeme import Lexeme


class Marker(object):
    def __init__(self, sentence, position):
        self.sentence = sentence
        self.position = position


class PlaceHolder(Lexeme):
    def __init__(self, word, position):
        super(PlaceHolder, self).__init__(word)
        self.position = position
        self.markers = []

    def __repr__(self):
        return "%d: '%s' (%d markers)" % (self.position, self.word.encode('utf-8'), len(self.markers))

#! coding: utf-8
import logging

import nltk

from .placeholder import PlaceHolder


def split_into_tokens(text, ignore_case=False):
    u"""Разбивает текст на слова"""
    if not text:
        return []
    try:
        if ignore_case:
            text = text.lower()
        pattern = '\*|(\w\-?)*\w+|\W+'
        return nltk.regexp_tokenize(text, pattern)
    except Exception as e:
        logging.warning(e, exc_info=1)


class Sentence(object):
    def __init__(self, text, placeholders=None):
        u"""
        :type  text: unicode
        :param text: текст предложения
        """
        self.text = text.replace(u'ё', u'е').replace(u'Ё', u'Е')
        self.place_holders = placeholders or []
        if not self.place_holders:
            for position, token in enumerate(split_into_tokens(self.text)):
                self.place_holders.append(PlaceHolder(token, position))

    def __repr__(self):
        return self.text.encode('utf-8')

    def __len__(self):
        return len(self.place_holders)

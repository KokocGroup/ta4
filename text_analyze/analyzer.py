#! coding: utf-8
from .placeholder import Marker
from .lexeme import Lexeme


class IAnalyzer(object):
    def mark(self, keyword, sentence):
        raise NotImplementedError


class ExactAnalyzer(IAnalyzer):
    def mark(self, keyword, sentence):
        stop = len(sentence.place_holders) - len(keyword.place_holders)
        for i, placeholder in enumerate(sentence.place_holders):
            if i > stop:
                break
            for j, ph in enumerate(keyword.place_holders):
                if not self.equals(ph, sentence.place_holders[i+j]):
                    break
            else:
                while j >= 0:
                    marker = Marker(keyword, j)
                    sentence.place_holders[i+j].markers.append(marker)
                    j -= 1

    def equals(self, ph, other):
        return ph.origin_word == other.origin_word


class SubformsAnalyzer(ExactAnalyzer):
    def equals(self, ph, other):
        u"""
        Порядок следования аргументов важен

        :param ph: placeholder из искомого слова
        :param other: placeholder из текста
        """
        return ph.is_special or (ph.get_all_normal_phorms() & other.get_all_normal_phorms())

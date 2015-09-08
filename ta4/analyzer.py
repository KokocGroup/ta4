#! coding: utf-8
from operator import attrgetter


class ExactAnalyzer(object):
    def get_sentence_placeholders(self, sentence):
        return filter(attrgetter('is_word'), sentence.place_holders)

    def mark(self, keyword, sentence, number):
        placeholders = self.get_sentence_placeholders(sentence)
        stop = len(placeholders) - len(keyword.place_holders)
        for i in xrange(len(placeholders)):
            if i > stop:
                break
            for j, ph in enumerate(keyword.place_holders):
                if not self.equals(ph, placeholders[i+j]):
                    break
            else:
                while j >= 0:
                    placeholders[i+j].add_marker(j, keyword, number)
                    j -= 1
                number += 1
        return number

    def equals(self, ph, other):
        return ph.origin_word == other.origin_word or ph.is_special


class SubformsAnalyzer(ExactAnalyzer):
    def get_sentence_placeholders(self, sentence):
        place_holders = super(SubformsAnalyzer, self).get_sentence_placeholders(sentence)
        return filter(attrgetter('is_important'), place_holders)

    def equals(self, ph, other):
        u"""
        Порядок следования аргументов важен

        :param ph: placeholder из искомого слова
        :param other: placeholder из текста
        """
        return ph.is_special or (ph.get_all_normal_phorms() & other.get_all_normal_phorms())

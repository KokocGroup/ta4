#! coding: utf-8
from operator import attrgetter

class ExactAnalyzer(object):
    def get_sentence_placeholders(self, sentence):
        return filter(attrgetter('is_word'), sentence.place_holders)

    def mark(self, keyword, sentence, number, should_mark=True):
        placeholders = self.get_sentence_placeholders(sentence)
        placeholders_count = len(placeholders)
        stop = placeholders_count - len(keyword.place_holders)
        i = 0
        while i < placeholders_count:
            if i > stop:
                break
            skipped_words = 0
            for j, ph in enumerate(keyword.place_holders):
                if ph.is_special:
                    # * - пропустить только одно значимое слово(и сколько угодно не значимых)
                    meaning_word = 0
                    while True:
                        if placeholders[i+j].is_important:
                            meaning_word += 1
                        # если встретили уже второе значимое слово
                        if meaning_word == 2 or i == placeholders_count - j - 1:
                            i -= 1
                            skipped_words -= 1
                            meaning_word -= 1
                            break
                        i += 1
                        skipped_words += 1
                    if not meaning_word:
                        break
                else:
                    index = i+j
                    if index >= placeholders_count or not self.equals(ph, placeholders[index]):
                        break
            else:
                if should_mark:
                    words_count = j + skipped_words
                    while words_count >= 0:
                        placeholders[i-skipped_words+words_count].add_marker(keyword, words_count, number)
                        words_count -= 1
                number += 1
            i += 1
        return number

    def equals(self, ph, other):
        return ph.word == other.word or ph.is_special


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

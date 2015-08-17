#! coding: utf-8
from operator import attrgetter


class Sentence(object):
    def __init__(self, text, placeholders=None):
        self.text = text
        self.place_holders = placeholders or []
        if not self.place_holders:
            from .utils import get_sentences
            _, sentences = get_sentences(self.text)
            self.place_holders = sentences[0].place_holders

    def __len__(self):
        return len(self.place_holders)

    def __repr__(self):
        return self.text.encode('utf-8')

    @property
    def is_exact_task(self):
        """
        Если задание по словоформам - вернёт False(например "[пластиковые] [окна]")
        """
        return not any(map(attrgetter('is_subform_word'), self.place_holders))

    @property
    def is_special(self):
        return any(map(attrgetter('is_special'), self.place_holders))

    def count(self, word):
        return len([ph for ph in self.place_holders if ph.word == word])

    @property
    def exact_count(self):
        return len(filter(lambda x: not x.is_subform_word, self.place_holders))

#! coding: utf-8
import itertools
from hashlib import md5

class Sentence(object):
    __slots__ = ['text', 'place_holders']

    def __init__(self, text, placeholders=None):
        self.text = text
        self.place_holders = placeholders or []
        if not self.place_holders:
            from .utils import get_sentences
            _, sentences = get_sentences(text)
            self.place_holders = sentences[0].place_holders

    def __len__(self):
        return len(self.place_holders)

    def __repr__(self):
        return self.text.encode('utf-8')

    def __iter__(self):
        for ph in self.place_holders:
            yield ph

    def __eq__(self, other):
        return isinstance(other, Sentence) and self.__hash__() == other.__hash__()

    def __hash__(self):
        return int(md5(self.text.encode('utf-8')).hexdigest(), 16)

    def __getitem__(self, item):
        return self.place_holders[item]

    @property
    def is_exact_task(self):
        """
        Если задание по словоформам - вернёт False(например "[пластиковые] [окна]")
        """
        for p in self.place_holders:
            if p.is_subform_word:
                return False
        return True

    @property
    def is_special(self):
        for p in self.place_holders:
            if p.is_special:
                return True

    def count(self, word):
        return len([ph for ph in self.place_holders if ph.word == word])

    @property
    def exact_count(self):
        return len(filter(lambda x: not x.is_subform_word, self.place_holders))

    @property
    def lexemes(self):
        return [u' '.join(lem) for lem in itertools.product(*[ph.lexemes for ph in self.place_holders])]
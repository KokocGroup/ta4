#! coding: utf-8
class Sentence(object):
    def __init__(self, text, placeholders=None):
        self.text = text
        self.place_holders = placeholders or []
        if not self.place_holders:
            from .utils import get_sentences
            _, sentences = get_sentences(self.text)
            self.place_holders = sentences[0].place_holders

    def __repr__(self):
        return self.text.encode('utf-8')

    def __len__(self):
        return len(self.place_holders)

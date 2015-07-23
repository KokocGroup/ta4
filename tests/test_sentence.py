#! coding: utf-8
from text_analyze.sentence import Sentence


def test_creation():
    test_table = [
        (u"Это обычный текст", 3),
        (u"Это обычный - текст", 4),
    ]
    for text, length in test_table:
        sentence = Sentence(text)
        assert sentence.text == text
        assert len(sentence) == length

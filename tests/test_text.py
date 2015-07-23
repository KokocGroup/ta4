#! coding: utf-8
from text_analyze.text import Text, TextHtml


def test_creation():
    text = Text(u"Это обычный текст. Из двух предложений.")
    assert len(text.sentences) == 2
    for sentence in text.sentences:
        assert len(sentence.place_holders) == 6


def test_html_creation():
    html = u'<p class="dialog"><span>Привет </span>Мир!</p>'
    text = TextHtml(html)
    assert len(text.sentences) == 1
    assert text.build_html() == html

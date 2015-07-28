#! coding: utf-8
from ta4.text import TextHtml


def test_creation():
    text = TextHtml(u"Это обычный текст. Из двух предложений.")
    assert len(text.sentences) == 2
    for sentence in text.sentences:
        assert len(sentence) == 3


def test_html_creation():
    html = u'<p class="dialog"><span>Привет </span>Мир!</p>'
    text = TextHtml(html)
    assert len(text.sentences) == 1
    assert text.build_html() == html


def test_simple_text_in_html_creation():
    html = u'Простое предложение. И * затем, следующее предложение'
    text = TextHtml(html)
    assert len(text.sentences) == 2
    assert text.build_html() == html

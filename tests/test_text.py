#! coding: utf-8
from ta4.text import TextHtml


def test_creation():
    text = TextHtml(u"Это обычный текст. Из двух предложений.")
    assert len(text) == 2
    for sentence in text:
        assert len(sentence) == 3


def test_html_creation():
    html = u'<p class="dialog"><span>Привет </span>Мир!</p>'
    text = TextHtml(html)
    assert len(text) == 1
    assert text.build_html() == html


def test_simple_text_in_html_creation():
    html = u'Простое предложение. И * затем, следующее предложение'
    text = TextHtml(html)
    assert len(text) == 2
    assert text.build_html() == html


def test_ignored_selectors():
    html = u'<span class="ice-del">Удалённое предложение. </span><span>А это нормальное затем, следующее предложение</span>'
    text = TextHtml(html, ignored_selectors=['span.ice-del'])
    assert len(text) == 1
    assert text.build_html() == html

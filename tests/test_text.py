#! coding: utf-8
from bs4 import BeautifulSoup

from ta4 import mark_with_words, find_words, get_marked_words
from ta4.text import TextHtml
from ta4.sentence import Sentence


def test_creation():
    text = TextHtml(u"Это обычный текст.Из двух предложений.")
    assert len(text) == 2
    for sentence in text:
        assert len(sentence) == 3


def test_html_creation():
    html = u'<p class="dialog"><span>Привет </span>Мир!</p>'
    text = TextHtml(html)
    assert len(text) == 1
    assert text.build_html() == html

    html = u"<span>Это обычный текст.Из двух</span> <span>предложений.</span>"
    text = TextHtml(html)
    assert len(text) == 2
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


def test_build_with_markers():
    word = Sentence(u'пластиковые окна')
    text = TextHtml(u'<p>купить пластиковые окна в москве</p>')
    mark_with_words([word], text)
    html = u'<p>купить <span data-markers="inactive-e4ca1dc74c4a889f31a1e24bb690b5c7">пластиковые </span>'\
           u'<span data-markers="inactive-e4ca1dc74c4a889f31a1e24bb690b5c7">окна </span>в москве</p>'
    assert text.build_html() == html

    find_words([word], text)
    html = u'<p>купить <span data-markers="e4ca1dc74c4a889f31a1e24bb690b5c7">пластиковые </span>'\
           u'<span data-markers="e4ca1dc74c4a889f31a1e24bb690b5c7">окна </span>в москве</p>'
    assert text.build_html() == html
    # проверим что множественный билд разметки ничего не сломает(там видоизменяется структура)
    assert text.build_html() == html

    # при повторной проверке уже отмаркированного списка - старые маркировки очищаются
    text = TextHtml(html)
    mark_with_words([word], text)
    find_words([word], text)
    assert text.build_html() == html


def test_build_with_ignored_tags():
    word = Sentence(u'пластиковые окна')
    html = u'<p><h2>купить пластиковые окна в москве</h2></p>'
    text = TextHtml(html, ignored_selectors=['h2'])
    mark_with_words([word], text)
    assert text.build_html() == html


def test_build_html_with_ol_tags():
    html = u''''<ol>
    <li>
        <p style="text-indent: 20px;">
            <span lang="ru-RU">First item.</span>
        </p>
    </li>
    <li>
        <p style="text-indent: 20px;">
            <span lang="ru-RU">Second item.</span>
        </p>
    </li>
</ol>'''
    text = TextHtml(html)
    mark_with_words([], text)
    html = text.build_html()
    bs = BeautifulSoup(html)
    assert len(bs.select('ol > li')) == 2, "There is two item in ordered list"


def test_clean_markers():
    text = TextHtml(u'купить пластиковые окна')
    mark_with_words([Sentence(u'купить пластиковые')], text)
    text.remove_markers()
    mark_with_words([Sentence(u'пластиковые окна')], text)
    counters = get_marked_words(text)
    assert len(counters) == 1


def test_span_with_spaces():
    text = u'<p>t <span> </span>e g</p>'
    html = TextHtml(text).build_html()
    assert text == html

    text = u"""<p style="text-indent: 20px;">T<span class="ice-ins ice-cts-1" data-changedata="" data-cid="5" data-last-change-time="1447922263562" data-time="1447922263562" data-userid="2" data-username="xsandr"> </span>e<span class="ice-ins ice-cts-1" data-changedata="" data-cid="6" data-last-change-time="1447922263968" data-time="1447922263968" data-userid="2" data-username="xsandr"> </span>s<span class="ice-ins ice-cts-1" data-changedata="" data-cid="7" data-last-change-time="1447922264341" data-time="1447922264341" data-userid="2" data-username="xsandr"> </span>t<span class="ice-ins ice-cts-1" data-changedata="" data-cid="8" data-last-change-time="1447922264695" data-time="1447922264695" data-userid="2" data-username="xsandr"> </span>i<span class="ice-ins ice-cts-1" data-changedata="" data-cid="9" data-last-change-time="1447922265110" data-time="1447922265110" data-userid="2" data-username="xsandr"> </span>n<span class="ice-ins ice-cts-1" data-changedata="" data-cid="10" data-last-change-time="1447922265485" data-time="1447922265485" data-userid="2" data-username="xsandr"> </span>g</p>"""
    html = TextHtml(text).build_html()
    assert text == html

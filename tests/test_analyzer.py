#! coding: utf-8
from text_analyze import mark_with_words
from text_analyze.text import TextHtml
from text_analyze.sentence import Sentence
from text_analyze.analyzer import ExactAnalyzer, SubformsAnalyzer


def common_check(word, text, placeholders=[]):
    i = 0
    for num, ph in enumerate(text.sentences[0].place_holders):
        if num in placeholders:
            assert ph.markers[0].sentence.text == word.text
            assert ph.markers[0].position == i
            i += 1
        else:
            assert ph.markers == []


def test_exact_analyzer():
    test_table = [
        (u'пластиковые окна', u'купить пластиковые окна в москве', [1, 2]),
        (u'пластиковые окна', u'много хороших слов купить пластиковые окна', [4, 5]),
        (u'пластиковое окно', u'купить пластиковые окна в москве', []),
        (u'пластиковые окна', u'купить пластиковые великолепные окна в москве', []),
    ]
    for word, text, placeholders in test_table:
        word = Sentence(word)
        text = TextHtml(text)
        mark_with_words([word], text, analyzers=[ExactAnalyzer()])
        common_check(word, text, placeholders)


def test_subform_analyzer():
    test_table = [
        (u'[пластиковое] [*] [окно]', u'купить пластиковые классные окна в москве', [1, 2, 3]),
        (u'[новогдняя] [ёлка]', u'купить новогднюю ёлку в москве недорого', [1, 2]),
        (u'[пластиковое] [*] [окно]', u'установка пластиковых окон', []),
        (u'[пластиковое] [*] [*] [окно]', u'пластиковые бронебойные анти-маскитные окна', [0, 1, 2, 3]),
        (u'[запчасть] [погрузчик]', u'запчасти для погрузчика', [0, 2]),
    ]
    for word, text, placeholders in test_table:
        word = Sentence(word)
        text = TextHtml(text)
        mark_with_words([word], text, analyzers=[SubformsAnalyzer()])
        common_check(word, text, placeholders)


def test_mark_multiple_words():
    words = [
        Sentence(u'купить пластиковые окна'),
        Sentence(u'пластиковые окна в москве')
    ]
    text = TextHtml(u'Здравствуйте! Я бы хотел купить пластиковые окна в москве, и конечно - недорого')
    mark_with_words(words, text, analyzers=[ExactAnalyzer()])
    phs = text.sentences[1].place_holders

    assert phs[3].markers[0].sentence.text == words[0].text
    assert phs[3].markers[0].position == 0
    assert phs[4].markers[0].sentence.text == words[0].text
    assert phs[4].markers[0].position == 1
    assert phs[5].markers[0].sentence.text == words[0].text
    assert phs[5].markers[0].position == 2

    assert phs[4].markers[1].sentence.text == words[1].text
    assert phs[4].markers[1].position == 0
    assert phs[5].markers[1].sentence.text == words[1].text
    assert phs[5].markers[1].position == 1
    assert phs[6].markers[0].sentence.text == words[1].text
    assert phs[6].markers[0].position == 2
    assert phs[7].markers[0].sentence.text == words[1].text
    assert phs[7].markers[0].position == 3


def test_build_with_markers():
    word = Sentence(u'пластиковые окна')
    text = TextHtml(u'<p>купить пластиковые окна в москве</p>')
    mark_with_words([word], text, analyzers=[ExactAnalyzer()])
    html = u'<p>купить <span data-markers="e4ca1dc74c4a889f31a1e24bb690b5c7">пластиковые </span>'\
           u'<span data-markers="e4ca1dc74c4a889f31a1e24bb690b5c7">окна </span>в москве</p>'
    assert text.build_html() == html
    assert text.build_html() == html

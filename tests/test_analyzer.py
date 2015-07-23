#! coding: utf-8
from text_analyze import analyze_text
from text_analyze.text import Text, TextHtml
from text_analyze.sentence import Sentence
from text_analyze.analyzer import ExactAnalyzer, SubformsAnalyzer


def test_exact_analyzer():
    word = Sentence(u'пластиковые окна')
    text = Text(u"купить пластиковые окна в москве")
    analyze_text([word], text, analyzers=[ExactAnalyzer()])
    assert text.sentences[0].place_holders[2].markers[0].sentence.text == word.text
    assert text.sentences[0].place_holders[2].markers[0].position == 0
    assert text.sentences[0].place_holders[3].markers[0].sentence.text == word.text
    assert text.sentences[0].place_holders[3].markers[0].position == 1
    assert text.sentences[0].place_holders[4].markers[0].sentence.text == word.text
    assert text.sentences[0].place_holders[4].markers[0].position == 2

    for i, ph in enumerate(text.sentences[0].place_holders):
        if i not in (2, 3, 4):
            assert ph.markers == []


def test_exact_analyzer2():
    word = Sentence(u'пластиковые окна')
    text = Text(u"много хороших слов купить пластиковые окна")
    analyze_text([word], text, analyzers=[ExactAnalyzer()])

    assert text.sentences[0].place_holders[4].markers[0].sentence.text == word.text
    assert text.sentences[0].place_holders[4].markers[0].position == 0
    assert text.sentences[0].place_holders[5].markers[0].sentence.text == word.text
    assert text.sentences[0].place_holders[5].markers[0].position == 1

    for i, ph in enumerate(text.sentences[0].place_holders):
        if i not in (4, 5):
            assert ph.markers == []


def test_exact_analyzer_reverse():
    word = Sentence(u'пластиковые окна')
    text = TextHtml(u"купить пластиковые окна в москве")
    analyze_text([word], text, analyzers=[ExactAnalyzer()])

    for i, ph in enumerate(text.sentences[0].place_holders):
        assert ph.markers == []


def test_exact_analyzer_reverse2():
    word = Sentence(u'пластиковые окна')
    text = TextHtml(u"купить пластиковые великолепные окна в москве")
    analyze_text([word], text, analyzers=[ExactAnalyzer()])

    for i, ph in enumerate(text.sentences[0].place_holders):
        assert ph.markers == []


def test_subform_analyzer():
    word = Sentence(u'[пластиковые] [*] [окна]')
    text = TextHtml(u"купить пластиковые классные окна в москве")
    analyze_text([word], text, analyzers=[SubformsAnalyzer()])

    assert text.sentences[0].place_holders[1].markers[0].sentence.text == word
    assert text.sentences[0].place_holders[1].markers[0].position == 0
    assert text.sentences[0].place_holders[2].markers[0].sentence.text == word
    assert text.sentences[0].place_holders[2].markers[0].position == 1
    assert text.sentences[0].place_holders[3].markers[0].sentence.text == word
    assert text.sentences[0].place_holders[3].markers[0].position == 2

    for i, ph in enumerate(text.sentences[0].place_holders):
        if i not in (1, 2, 3):
            assert ph.markers == []

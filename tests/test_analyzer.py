#! coding: utf-8
from text_analyze import analyze_text
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
    word = Sentence(u'пластиковые окна')
    text = TextHtml(u"купить пластиковые окна в москве")
    analyze_text([word], text, analyzers=[ExactAnalyzer()])
    common_check(word, text, [1, 2])


def test_exact_analyzer2():
    word = Sentence(u'пластиковые окна')
    text = TextHtml(u"много хороших слов купить пластиковые окна")
    analyze_text([word], text, analyzers=[ExactAnalyzer()])
    common_check(word, text, [4, 5])


def test_exact_analyzer_reverse():
    word = Sentence(u'пластиковое окно')
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
    common_check(word, text, [1, 2, 3])


def test_new_letter():
    word = Sentence(u'[новогдняя] [ёлка]')
    text = TextHtml(u"купить новогднюю ёлку в москве недорого")
    analyze_text([word], text, analyzers=[SubformsAnalyzer()])
    common_check(word, text, [1, 2])

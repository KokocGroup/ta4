#! coding: utf-8
from ta4 import mark_with_words, find_words, group_markers, merge_filter
from ta4.text import TextHtml
from ta4.sentence import Sentence


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
        (u'пластиковые * окна', u'купить пластиковые великолепные окна в москве', [1, 2, 3])
    ]
    for word, text, placeholders in test_table:
        word = Sentence(word)
        text = TextHtml(text)
        mark_with_words([word], text)
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
        mark_with_words([word], text)
        common_check(word, text, placeholders)


def test_mark_multiple_words():
    words = [
        Sentence(u'купить пластиковые окна'),
        Sentence(u'пластиковые окна в москве')
    ]
    text = TextHtml(u'Здравствуйте! Я бы хотел купить пластиковые окна в москве, и конечно - недорого')
    mark_with_words(words, text)
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


def test_group_markers():
    markers = [
        (Sentence(u'test1'), {'min': 0, 'max': 4}),
        (Sentence(u'test2'), {'min': 1, 'max': 5}),
        (Sentence(u'test3'), {'min': 1, 'max': 5}),
        (Sentence(u'test4'), {'min': 4, 'max': 7}),
        (Sentence(u'test5'), {'min': 9, 'max': 12}),
        (Sentence(u'test6'), {'min': 9, 'max': 11}),
        (Sentence(u'test7'), {'min': 10, 'max': 12}),
        (Sentence(u'test8'), {'min': 9, 'max': 10}),
        (Sentence(u'test9'), {'min': 11, 'max': 12})
    ]
    results = list(group_markers(markers))
    assert len(results) == 2
    assert results[0] == [markers[0], markers[1], markers[3]]
    assert results[1] == [markers[4]]

    markers = [
        (Sentence(u'test1'), {'min': 0, 'max': 4}),
        (Sentence(u'test2'), {'min': 5, 'max': 7}),
        (Sentence(u'test3'), {'min': 9, 'max': 12}),
    ]
    results = list(group_markers(markers))
    assert len(results) == 3
    assert results[0] == markers[:1]
    assert results[1] == markers[1:2]
    assert results[2] == markers[2:]


def test_merging_markers():
    markers = [
        (Sentence(u'test1'), {'min': 0, 'max': 0}),
        (Sentence(u'test2'), {'min': 0, 'max': 1}),
        (Sentence(u'test3'), {'min': 0, 'max': 0}),
    ]
    result = merge_filter(markers)
    assert result == markers[:2]

    markers = [
        (Sentence(u'test1'), {'min': 2, 'max': 4}),
        (Sentence(u'test2'), {'min': 1, 'max': 5}),
        (Sentence(u'test3'), {'min': 2, 'max': 3}),
    ]
    result = merge_filter(markers)
    assert result == markers[:2]


def test_find_words_without_intersection():
    test_table = [
        (
            {u'купить пластиковые окна': 1, u'пластиковые окна в москве': 1},
            u'Купить пластиковые окна, причём недорого. Найти пластиковые окна в москве не так уж и просто.'
        ),
        (
            {u'[купить] [*] [окна]': 1, u'[пластиковые] [окна] [москве]': 1},
            u'Я хочу купить пластиковые окна, причём недорого. Найти пластиковые окна в москве не так уж и просто.'
        ),
        (
            {u'[купить] [*] [окна]': 2},
            u'Я хочу купить, офигенные окна, причём недорого. Купить пластиковые окна в москве не так уж и просто.'
        ),
        (
            {u'[САНАТОРИЙ] [РОССИЯ]': 1, u'санатории россии': 1},
            u'На нашей теретории лучшие санатории России. Санаторий в России хорошо подходит для '
            u'оздаровления организма. Все вранье, санаторий - это плохо. Особенно в России.'
        ),
        (
            {u"[МАШИНА]": 2, u"МАШИНЫ": 1},
            u'Машину угнали! В машине были все документы! У машины стояло 2 странных парня'
        ),
        (
            {u"[БАНК]": 1}, u'Я должен денег банку!'
        ),
        (
            {u'купить * шар': 1, u'купить зеленый шар': 1},
            u'Всем привет, я хотел бы купить оранжевый шар для себя. И еще нужно купить зеленый шар для друзей.'
        )
    ]
    for task, text in test_table:
        words = map(Sentence, task.keys())
        text = TextHtml(text)
        mark_with_words(words, text)
        # так как пересечений нет, то и дополненного задания не будет
        result, additional_words = find_words(words, text)
        assert additional_words == {}
        assert result == task


def test_merge():
    test_table = [
        ({u'окна в москве': 1, u'[купить] [окна] [москва] [недорого]': 1},
         u'я бы хотел купить окна в москве недорого, и без проблем',
         {u'ОКНА В МОСКВЕ': 1}),
    ]
    for task, text, new_task in test_table:
        words = map(Sentence, task.keys())
        text = TextHtml(text)
        mark_with_words(words, text)
        result, additional_words = find_words(words, text)
        assert additional_words == new_task
        assert result == task


def test_find_words_with_intersections():
    test_table = [
        (
            {u'купить пластиковые окна': 1, u'пластиковые окна в москве': 1},
            u'купить пластиковые окна в москве',
            {u'ПЛАСТИКОВЫЕ ОКНА': 1}
        ),
        (
            {u'пластиковые окна': 1, u'[пластиковые] [окна]': 0},
            u'купить пластиковые окна в москве',
            {}
        ),
        (
            {
                u'быстро выгодно купить качественное пластиковое': 1,
                u'выгодно купить качественное пластиковое окно': 1,
                u'пластиковое окно в москве': 1,
            },
            u'быстро выгодно купить качественное пластиковое окно в москве',
            {
                u'ВЫГОДНО КУПИТЬ КАЧЕСТВЕННОЕ ПЛАСТИКОВОЕ': 1,
                u'ПЛАСТИКОВОЕ ОКНО': 1
            }
        ),
        (
            {u'[ПОЛИЭТИЛЕНОВЫЙ] [ЗЕЛЕНЫЙ]': 1, u'[ПОЛИЭТИЛЕНОВЫЙ]': 2, u'ПОЛИЭТИЛЕНОВЫЙ': 2},
            u"полиэтиленовый зеленый пакет болтался на дереве.Полиэтиленовый пакет. Полиэтиленовая лямка! Полиэтиленовая!",
            {u'ПОЛИЭТИЛЕНОВЫЙ': 1}
        ),
        (
            {u'купить пластиковые окна': 1, u'[купить] [*] [окна] [москва]': 1},
            u"купить пластиковые окна это круто. Хотите купить накрутейшие окна в москве?.",
            {}
        ),
        (
            {u'запчасть для погрузчика': 1, u'[запчасть] [*] [погрузчик]': 1, u'запчасть на погрузчик': 1},
            u"запчасть для погрузчика. запчасть зеленого погрузчика. запчасть на погрузчик.",
            {}
        ),
        (
            {u'преобрести уаз бортовой': 1, u'уаз бортовой': 0, u'уаз': 0, u'бортовой': 0},
            u'я хочу преобрести уаз бортовой в москве',
            {}
        )
    ]
    for task, text, new_task in test_table:
        words = map(Sentence, task.keys())
        text = TextHtml(text)
        mark_with_words(words, text)
        result, additional_words = find_words(words, text)
        assert task == result
        assert new_task == additional_words


def test_analyze_high_index_intersection():
    text = TextHtml(u"Я бы хотел приобрести фронтальные погрузчики!")
    words = map(Sentence, [u'хотел приобрести фронтальные', u'приобрести фронтальные погрузчики'])
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert additional_words != {}
    assert u'' not in additional_words


def test_multiple_words_in_one_sentence():
    text = TextHtml(u"Машина врезалась в припаркованые машины!")
    word = Sentence(u'[машина]')
    mark_with_words([word], text)
    result, _ = find_words([word], text)
    assert result.values()[0] == 2


def test_english_titles():
    word = Sentence(u'[бензопила] [husqvarna]')
    text = TextHtml(u'Бензопилы husqvarna - одни из лучших')
    mark_with_words([word], text)
    result, _ = find_words([word], text)
    assert result.values()[0] == 1


def test_asterisk_in_exact_word():
    words = map(Sentence, [u'игры [*] разработчика', u'игры'])
    text = TextHtml(u'игры находит, но не игры русского разработчика')
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert additional_words == {}
    assert result[u'игры'] == 1
    assert result[u'игры [*] разработчика'] == 1
    html = u"""<span data-markers="d203f33bb6e9ec9d0238e29d4ccfc97e">игры </span>находит, но не <span data-markers="f350ba1c1103dc72275a99ccc134dc3f inactive-d203f33bb6e9ec9d0238e29d4ccfc97e">игры </span><span data-markers="f350ba1c1103dc72275a99ccc134dc3f">русского </span><span data-markers="f350ba1c1103dc72275a99ccc134dc3f">разработчика</span>"""
    assert text.build_html() == html

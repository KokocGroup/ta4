#! coding: utf-8
import pytest

from ta4 import mark_with_words, find_words, merge_filter, get_marked_words
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


@pytest.mark.parametrize("word,text,expected", [
    (u'пластиковые окна', u'купить пластиковые окна в москве', [1, 2]),
    (u'пластиковые окна', u'много хороших слов купить пластиковые окна', [4, 5]),
    (u'пластиковое окно', u'купить пластиковые окна в москве', []),
    (u'пластиковые окна', u'купить пластиковые великолепные окна в москве', []),
    (u'пластиковые * окна', u'купить пластиковые великолепные окна в москве', [1, 2, 3])
])
def test_exact_analyzer(word, text, expected):
    word = Sentence(word)
    text = TextHtml(text)
    mark_with_words([word], text)
    common_check(word, text, expected)


@pytest.mark.parametrize("word,text,expected", [
    (u'[пластиковое] [*] [окно]', u'купить пластиковые классные окна в москве', [1, 2, 3]),
    (u'[новогдняя] [ёлка]', u'купить новогднюю ёлку в москве недорого', [1, 2]),
    (u'[пластиковое] [*] [окно]', u'установка пластиковых окон', []),
    (u'[пластиковое] [*] [*] [окно]', u'пластиковые бронебойные анти-маскитные окна', [0, 1, 2, 3]),
    (u'[запчасть] [погрузчик]', u'запчасти для погрузчика', [0, 2]),
])
def test_subform_analyzer(word, text, expected):
    word = Sentence(word)
    text = TextHtml(text)
    mark_with_words([word], text)
    common_check(word, text, expected)


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


def test_merging_markers():
    markers = [
        (Sentence(u'test1'), {'min': 0, 'max': 0}),
        (Sentence(u'test1 test2'), {'min': 0, 'max': 1}),
        (Sentence(u'[test1]'), {'min': 0, 'max': 0}),
    ]
    result, _ = merge_filter(markers, Sentence(u"test1 test2"))
    assert result == markers[:2]

    markers = [
        (Sentence(u'b c d e f'), {'min': 1, 'max': 5}),
        (Sentence(u'a b c'), {'min': 0, 'max': 2}),
        (Sentence(u'c d e'), {'min': 2, 'max': 4}),
    ]
    result, _ = merge_filter(markers, Sentence(u"a b c d e f g"))
    assert result == markers[:2]


@pytest.mark.parametrize("task,text", [
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
])
def test_find_words_without_intersection(task, text):
    words = map(Sentence, task.keys())
    text = TextHtml(text)
    mark_with_words(words, text)
    # так как пересечений нет, то и дополненного задания не будет
    result, additional_words = find_words(words, text)
    assert additional_words == {}
    assert result == task


@pytest.mark.parametrize("task,text,new_task", [
    ({u'окна в москве': 0, u'[купить] [окна] [москва] [недорого]': 1},
     u'я бы хотел купить окна в москве недорого, и без проблем',
     {}),
])
def test_merge(task, text, new_task):
    words = map(Sentence, task.keys())
    text = TextHtml(text)
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert additional_words == new_task
    assert result == task


@pytest.mark.parametrize("task,text,new_task", [
    (
        {u'купить пластиковые окна': 1, u'пластиковые окна в москве': 1},
        u'купить пластиковые окна в москве',
        {u'пластиковые окна': 1}
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
            u'выгодно купить качественное пластиковое': 1,
            u'пластиковое окно': 1
        }
    ),
    (
        {u'[ПОЛИЭТИЛЕНОВЫЙ] [ЗЕЛЕНЫЙ]': 1, u'[ПОЛИЭТИЛЕНОВЫЙ]': 2, u'ПОЛИЭТИЛЕНОВЫЙ': 1},
        u"полиэтиленовый зеленый пакет болтался на дереве.Полиэтиленовый пакет. Полиэтиленовая лямка! Полиэтиленовая!",
        {}
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
])
def test_find_words_with_intersections(task, text, new_task):
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
    html = u"""<span data-markers="d203f33bb6e9ec9d0238e29d4ccfc97e">игры </span>находит, но не <span data-markers="f350ba1c1103dc72275a99ccc134dc3f inactive-d203f33bb6e9ec9d0238e29d4ccfc97e target-d203f33bb6e9ec9d0238e29d4ccfc97e">игры </span><span data-markers="f350ba1c1103dc72275a99ccc134dc3f target-d203f33bb6e9ec9d0238e29d4ccfc97e">русского </span><span data-markers="f350ba1c1103dc72275a99ccc134dc3f target-d203f33bb6e9ec9d0238e29d4ccfc97e">разработчика</span>"""
    assert text.build_html() == html


def test_html_lists():
    text = u"""
    <p>Виды имплантации зубов:</p>
    <ul>
        <li>Какая то имплантация</li>
        <li>Базальная имплантация</li>
    </ul>
    <p>Имплантация зубов имеет разные технологии.</p>
    """
    text = TextHtml(text)
    task = {u'[имплантация] [*] [зубов]': 0}
    words = map(Sentence, task.keys())
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result == task


def test_punctuation_positive():
    words = [Sentence(u'знаки препинания')]
    text = TextHtml(u"""
    <p>знаки – препинания</p>
    <p>знаки, препинания</p>
    <p>знаки: препинания</p>
    <p>знаки (препинания</p>
    <p>знаки; препинания</p>
    <p>знаки "препинания</p>
    """)
    task = {u'знаки препинания': 6}
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result == task


def test_punctuation_negative():
    words = [Sentence(u'знаки препинания')]
    text = TextHtml(u"""
    <p>знаки-препинания</p>
    <p>знаки. препинания</p>
    <p>знаки! препинания</p>
    <p>знаки? препинания</p>
    <p><span><span>знаки</span></span></p>
    <p><span><span>препинания</span></span></p>
    """)
    task = {u'знаки препинания': 0}
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result == task


def test_paragraph_break():
    text = TextHtml(u"""
    <p style="text-indent: 20px;">Дентальная&nbsp;<span data-markers="badef16d17cb3f15a6eae4e11b39ef9b" class="highlightedText">имплантация</span><br>Бескровная&nbsp;<span data-markers="badef16d17cb3f15a6eae4e11b39ef9b" class="highlightedText">имплантация</span><br>Лазерная&nbsp;<span data-markers="badef16d17cb3f15a6eae4e11b39ef9b" class="highlightedText">имплантация</span><br>Базальная&nbsp;<span data-markers="68d827caec2e46d49ea561212476052f inactive-badef16d17cb3f15a6eae4e11b39ef9b target-f7cf930ddf8a402b1c0d559e97932ad6 target-7bc22675ef51be0fb916f66f8b61013f target-badef16d17cb3f15a6eae4e11b39ef9b target-1ec1ca7a93460e9f12d8c84116914067" class="highlightedText">имплантация</span><br><br></p>
    <p style="text-indent: 20px;"><span data-markers="68d827caec2e46d49ea561212476052f inactive-7bc22675ef51be0fb916f66f8b61013f inactive-badef16d17cb3f15a6eae4e11b39ef9b target-f7cf930ddf8a402b1c0d559e97932ad6 target-7bc22675ef51be0fb916f66f8b61013f target-badef16d17cb3f15a6eae4e11b39ef9b target-1ec1ca7a93460e9f12d8c84116914067" class="highlightedText">Имплантация</span>&nbsp;<span data-markers="68d827caec2e46d49ea561212476052f inactive-1ec1ca7a93460e9f12d8c84116914067 inactive-f7cf930ddf8a402b1c0d559e97932ad6 inactive-7bc22675ef51be0fb916f66f8b61013f target-f7cf930ddf8a402b1c0d559e97932ad6 target-7bc22675ef51be0fb916f66f8b61013f target-badef16d17cb3f15a6eae4e11b39ef9b target-1ec1ca7a93460e9f12d8c84116914067" class="highlightedText">зубов</span>&nbsp;имеет разные технологии. Выбор определяет состояние костной ткани и дёсен пациента; место, где расположен&nbsp;<span data-markers="1ec1ca7a93460e9f12d8c84116914067" class="highlightedText">зуб;</span>&nbsp;количество&nbsp;<span data-markers="inactive-1ec1ca7a93460e9f12d8c84116914067 f7cf930ddf8a402b1c0d559e97932ad6 target-1ec1ca7a93460e9f12d8c84116914067" class="highlightedText">зубов</span>&nbsp;для восстановления; период времени, прошедший с момента потери&nbsp;<span data-markers="1ec1ca7a93460e9f12d8c84116914067" class="highlightedText">зуба.</span>&nbsp;Выбор технологии&nbsp;<span data-markers="7bc22675ef51be0fb916f66f8b61013f inactive-badef16d17cb3f15a6eae4e11b39ef9b inactive-7d63159b48a8683402e56a8fcc4cb772 target-f7cf930ddf8a402b1c0d559e97932ad6 target-7d63159b48a8683402e56a8fcc4cb772 target-badef16d17cb3f15a6eae4e11b39ef9b target-1ec1ca7a93460e9f12d8c84116914067" class="highlightedText">имплантации</span>&nbsp;<span data-markers="inactive-1ec1ca7a93460e9f12d8c84116914067 inactive-f7cf930ddf8a402b1c0d559e97932ad6 7bc22675ef51be0fb916f66f8b61013f target-f7cf930ddf8a402b1c0d559e97932ad6 target-7d63159b48a8683402e56a8fcc4cb772 target-badef16d17cb3f15a6eae4e11b39ef9b target-1ec1ca7a93460e9f12d8c84116914067" class="highlightedText">зубов</span>&nbsp;предварительно осуществляется при первичном осмотре и окончательно — по результатам компьютерной диагностики.</p>
    """)

    task = {u'[имплантация] [*] [зубов]': 0}
    words = map(Sentence, task.keys())
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result == task


def test_analyze_asterisk():
    words = [Sentence(u'услуги * квартир')]
    text = TextHtml(u"""
    <li>услуги по ремонту квартир</li>
    <li>услуги отделки для квартир</li>
    <li>услуги по уборке для квартир более 100 кв метров</li>

    <li>услуги для уборки в роскошной квартир</li>
    <li>услуги в квартир</li>
    <li>услуги для квартир</li>
    <li>услуги квартир</li>
    """)
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result[u'услуги * квартир'] == 3


def test_some_text():
    text = TextHtml(u"""
<h1>Ремонт кофемашин метро Проспект Вернадского</h1>

<title>Ремонт кофемашин у метро Проспект Вернадского вызов мастера на дом в Москве, Сервис Хоум</title>

Компания «СервисХоум» предлагает качественный ремонт кофемашин на дому. Устранение неполадок техники осуществляется оперативно и профессионально.

Мы ремонтируем широкий спектр различных кофемашин у метро Проспект Вернадского и выполняем свою работу качественно. Наши специалисты:

приедут по вашему вызову в назначенное время;
произведут качественный ремонт и замену деталей аппарата;
выполнят работы быстро и по выгодной стоимости.
Перед тем как провести ремонт, осуществляется диагностика кофемашин в районе Проспекта Вернадского, и только после нее производится устранение неисправностей. Также специалисты «СервисХоум» проводят профилактические работы, продлевающие срок службы техники надолго.

Обращаясь в «СервисХоум», вы можете быть полностью уверены в том, что наши специалисты выполнят ремонт вашей кофемашины оперативно и профессионально.

Чтобы вызвать специалиста на дом, нужно оставить заявку или позвонить нам по номеру +7 (495) 212 0593.
    """, ignored_tags=[('title', ), ('h1', ), ('h2', ), ('h3', ), ('span', {'class': 'ice-del'})])
    words = map(Sentence, [
        u'[КОФЕМАШИН] [*] [ПРОСПЕКТ]',
        u'проспект вернадского',
        u'вернадского'])
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result[u'[КОФЕМАШИН] [*] [ПРОСПЕКТ]'] == 2
    assert result[u'вернадского'] == 1
    assert u'вернадского' not in additional_words


def test_word_good():
    text = TextHtml(u"""
        А наша компания поможет вам с выбором лучшего санатория или пансионата.
        Рейтинг лучших санаторно-курортных комплексов вы можете увидеть на нашем сайте.
    """)
    words = map(Sentence, [
        u'[ХОРОШИЙ]',
        u'[ЛУЧШИЙ]',
    ])
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result[u'[ХОРОШИЙ]'] == 0
    assert result[u'[ЛУЧШИЙ]'] == 2


def test_word_child():
    text = TextHtml(u"Дети наше будующее! Ребёнок не должен оставаться дома один")
    words = map(Sentence, [
        u'[ДЕТИ]',
        u'[РЕБЁНОК]',
    ])
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result[u'[ДЕТИ]'] == 1
    assert result[u'[РЕБЁНОК]'] == 1


def test_html_with_strong():
    text = TextHtml(u"<p>Екарта для Екатеринбурга</p><p>Карту для оплаты проезда.</p>")
    assert len(text.sentences) == 2
    words = map(Sentence, [
        u'карту'
    ])
    mark_with_words(words, text)
    result, additional_words = find_words(words, text)
    assert result[u'карту'] == 1


def test_get_marked_words():
    text = TextHtml(u"Купить пластиковые окна в москве и не дорого. Деревянные окна под заказ")
    original_words = [
        u'купить * окна',
        u'пластиковые окна в москве',
        u'деревянные окна',
    ]
    words = map(Sentence, original_words)
    mark_with_words(words, text)
    marked = get_marked_words(text)
    for word in original_words:
        assert marked[word] == 1


@pytest.mark.parametrize("words, text, phantoms", [
    (
        [u'купить пластиковые окна', u'пластиковые окна в москве'],
        u'купить пластиковые окна в москве',
        [u'пластиковые окна']
    ),
    (
        [u'[купить] [*] [окна]', u'пластиковые окна в москве'],
        u'купить пластиковые окна в москве',
        [u'пластиковые окна']
    ),
    (
        [u'[купить] [*] [окна]', u'[пластиковые] [*] [москве]'],
        u'купить пластиковые окна в москве',
        [u'пластиковые окна']
    ),
    (
        [u'купить пластиковые окна', u'[пластиковые] [*] [москве]'],
        u'купить пластиковые окна в москве',
        [u'пластиковые окна']
    ),
    (
        [u'пластиковые окна в москве', u'[окна] [москве] [сегодня]'],
        u'пластиковые окна в москве сегодня холодно',
        [u'окна в москве']
    ),
])
def test_find_phantom_groups(words, text, phantoms):
    words = map(Sentence, words)
    text = TextHtml(text)
    mark_with_words(words, text)
    _, additional_words = find_words(words, text)
    assert additional_words.keys() == phantoms

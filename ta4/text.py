# coding=utf-8
from copy import deepcopy
from operator import attrgetter
from bs4 import BeautifulSoup, Tag
from lxml.html import diff

from .utils import get_sentences


IGNORED_TAG_TEMPLATE = u'ignored_{}'


class TextHtml(object):
    def __init__(self, html, ignored_selectors=[]):
        self.bs = BeautifulSoup(self.prepare_html(html), 'html.parser')
        self.text = html
        self.sentences = []
        self.ignored_element_map = {}

        for selector in ignored_selectors:
            for elem in self.bs.select(selector):
                i = len(self.ignored_element_map) + 1
                tag = Tag(name=IGNORED_TAG_TEMPLATE.format(i))
                self.ignored_element_map[tag] = elem
                elem.replace_with(tag)

        # remove old markers
        for element in self.bs.findAll(attrs={'data-markers': True}):
            element.unwrap()

        self.text_after_replacement = unicode(self.bs)
        self.structure, self.sentences = get_sentences(unicode(self.bs))

    def __iter__(self):
        for sentence in self.sentences:
            yield sentence

    def __len__(self):
        return len(self.sentences)

    def __repr__(self):
        return self.text_after_replacement.encode('utf-8')

    def prepare_html(self, html):
        return html.replace('<br>', '<br/>').replace('<hr>', '<hr/>').replace('</br>', '')\
                   .replace('</hr>', '').replace("&nbsp;", "<nbsp/>")

    def build_html(self):
        u"""
        build_html может вызываться несколько раз, и так как мы добавляем маркеры в теги,
        то надо копировать структуру
        """
        html = []
        for tokens, place_holder in deepcopy(self.structure):
            if place_holder and place_holder.markers:
                markers = u' '.join(map(attrgetter('hash'), place_holder.markers))
                targets = [u'target-'+h for marker in place_holder.markers for h in marker.target_sentence]
                targets = u' '.join(targets)
                open_tag = u'<span data-markers="%s">' % (u' '.join([markers, targets]).strip())
                tokens[0].pre_tags.append(open_tag)
                tokens[-1].post_tags.insert(0, u'</span>')
            html.append(u''.join(diff.expand_tokens(tokens)))

        html = u''.join(html)
        html = html.replace("&nbsp;", "<nbsp/>")
        html = BeautifulSoup(self.prepare_html(html), 'html.parser')

        for ignored_tag, original_tag in self.ignored_element_map.items():
            tag = html.find(ignored_tag.name, attr=ignored_tag.attrs, text=ignored_tag.text)
            if tag:
                tag.replace_with(original_tag)
        return unicode(html).replace(u"<nbsp></nbsp>", u"\xa0")

# coding=utf-8
import re
import string
import logging

from bs4 import BeautifulSoup, Tag

from lxml.html import diff

from . import tokenizer
from .sentence import Sentence
from .placeholder import PlaceHolder


IGNORED_TAG_TEMPLATE = u'ignored_{}'

SPACE_REGEXP = re.compile('^(\s|&nbsp;)+$', flags=re.I | re.M)


class Text(object):
    def __init__(self, text):
        self.text = text
        self.sentences = map(Sentence, self.split_into_sentences(self.text))

    def __iter__(self):
        for sentence in self.sentences:
            yield sentence

    def split_into_sentences(cls, text):
        if not text:
            return []
        try:
            sent_token = tokenizer.tokenize(text)
            sentences = []
            for sent in sent_token:
                for passage in re.split(r"\s{3,}", sent):
                    sentences.append(passage)
            return sentences
        except Exception, error:
            logging.exception(error)

    def __repr__(self):
        u"""Текстовое представление текста
        """
        return self.text.encode('utf-8')


def is_token_end(token):
    if SPACE_REGEXP.match(token.trailing_whitespace) or \
       token.trailing_whitespace in (u' ', u'\xa0') or \
       (token and token[-1] in string.punctuation) or \
       (token.post_tags and token.post_tags[-1][-1] == u' '):
        return True

    return False


def tokens_generator(tokens):
    result = []
    length = len(tokens) - 1

    for i, token in enumerate(tokens):
        result.append(token)
        next_one = None
        if i < length:
            next_one = tokens[i+1]
        if is_token_end(token) or (next_one and '<br>' in next_one.pre_tags) or (next_one and '<nbsp>' in next_one.pre_tags):
            yield result
            result = []
    else:
        yield result


class TextHtml(Text):

    END_CHRS = u'.?!'

    def __init__(self, html, ignored_selectors=[]):
        self.bs = BeautifulSoup(self.prepare_html(html), 'html.parser')
        self.text = self.bs.get_text()  # TODO нужно ли?
        self.sentences = []
        self.ignored_element_map = {}
        ignored_id = 1
        for selector in ignored_selectors:
            for elem in self.bs.select(selector):
                tag = Tag(name=IGNORED_TAG_TEMPLATE.format(ignored_id))
                self.ignored_element_map[tag] = elem
                elem.replace_with(tag)
                ignored_id += 1

        self.structure = []
        sentence = u''
        place_holders = []

        tokens = diff.tokenize(unicode(self.bs))
        for position, word_tokens in enumerate(tokens_generator(tokens)):
            word = u''.join(map(unicode, word_tokens))

            if word:
                last_token = word_tokens[-1]
                sentence += word + last_token.trailing_whitespace
                try:
                    place_holder = PlaceHolder(word.rstrip(self.END_CHRS), position)
                    place_holders.append(place_holder)
                except AttributeError:
                    place_holder = None
                self.structure.append([word_tokens, place_holder])
                if last_token[-1] in self.END_CHRS:
                    self.sentences.append(Sentence(sentence, place_holders))
                    sentence = u''
                    place_holders = []
            else:
                self.structure.append([word_tokens, None])
        else:
            if sentence:
                self.sentences.append(Sentence(sentence, place_holders))

    def prepare_html(self, html):
        return html.replace('<br>', '<br/>').replace('<hr>', '<hr/>').replace('</br>', '')\
                   .replace('</hr>', '').replace("&nbsp;", "<nbsp/>")

    def build_html(self):
        html = u''
        for tokens, place_holder in self.structure:
            if place_holder and place_holder.markers:
                open_tag = u'<span data-markers="%s">' % u' '.join(place_holder.markers)
                tokens[0].pre_tags.append(open_tag)
                tokens[-1].post_tags.insert(0, u'</span>')
            html += u''.join(diff.expand_tokens(tokens))

        html = html.replace("&nbsp;", "<nbsp/>")
        html = BeautifulSoup(self.prepare_html(html), 'html.parser')

        for ignored_tag, original_tag in self.ignored_element_map.items():
            tag = html.find(ignored_tag.name, attr=ignored_tag.attrs, text=ignored_tag.text)
            if tag:
                tag.replace_with(original_tag)
        return unicode(html).replace(u"<nbsp></nbsp>", u"\xa0")

    def __repr__(self):
        return self.bs.get_text().encode('utf-8')

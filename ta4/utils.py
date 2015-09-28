#! coding: utf-8
import re
import string

from lxml.html import diff

from .sentence import Sentence
from .placeholder import PlaceHolder

SENTENCES_END = u'.?!'
SENTENCES_END_TAGS = {'</p>', '</li>', '</ul>', '</ol>'}
SPACE_REGEXP = re.compile('^(\s|&nbsp;)+$', flags=re.I | re.M)


def is_token_end(token):
    if SPACE_REGEXP.match(token.trailing_whitespace) or \
       token.trailing_whitespace in (u' ', u'\xa0') or \
       (token and token[-1] in string.punctuation) or \
       (token.post_tags and token.post_tags[-1][-1] == u' '):
        return True

    return False


def tokens_generator(tokens):
    u"""
    Первоначальное разбиение на теги
    """
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


def split_token(word_tokens):
    """
    Разбивает токены на куски например из ["привет.Как "] сделает [["привет."], ["Как"]]
    """
    results = []
    tokens = []
    for token in word_tokens:
        i = 0
        length = len(token)
        while i < length:
            if token[i] in SENTENCES_END:
                new_token = diff.token(token[:i+1])
                new_token.pre_tags = token.pre_tags
                post_tags = token.post_tags
                if i == length - 1:
                    # мы дошли до конца и встретили символ окончания предложения
                    new_token.post_tags = token.post_tags
                    new_token.trailing_whitespace = token.trailing_whitespace
                    post_tags = []
                tokens.append(new_token)
                results.append(tokens)
                tokens = []
                token = diff.token(token[i+1:], post_tags=post_tags,
                                   trailing_whitespace=token.trailing_whitespace)
                length = len(token)
                i = 0
            i += 1
        # если встретили пустой тег - скипаем его
        if len(token) == 0 and not token.pre_tags and not token.post_tags:
            continue
        tokens.append(token)
    if tokens:
        results.append(tokens)
    return results


def is_sentence_end(last_token):
    if last_token:
        last_tags = set(map(unicode.strip, map(unicode, last_token.post_tags)))
        if (last_token[-1] in SENTENCES_END or
           last_tags.intersection(SENTENCES_END_TAGS)):
            return True
    return False


def is_sentence_begin(first_token):
    if first_token:
        pre_tags = set(map(unicode.strip, map(unicode, first_token.pre_tags)))
        if pre_tags.intersection({u'<br>', u'</br>'}):
            return True
    return False


def get_sentences(text):
    structure = []
    sentences = []
    place_holders = []
    sentence = u''
    tokens = diff.tokenize(text)
    position = 0
    for word_tokens in tokens_generator(tokens):
        if not word_tokens:
            structure.append([word_tokens, None])
            position += 1

        for tokens in split_token(word_tokens):
            word = u''.join(map(unicode, tokens))
            word = word.rstrip(SENTENCES_END)
            first_token = tokens[0]
            if is_sentence_begin(first_token) and place_holders:
                sentences.append(Sentence(sentence, place_holders))
                sentence = u''
                place_holders = []

            last_token = tokens[-1]
            sentence += word + last_token.trailing_whitespace
            place_holder = PlaceHolder(word, position)
            place_holders.append(place_holder)
            structure.append([tokens, place_holder])

            if is_sentence_end(last_token):
                sentences.append(Sentence(sentence, place_holders))
                sentence = u''
                place_holders = []
            position += 1
    else:
        if sentence:
            sentences.append(Sentence(sentence, place_holders))
    return structure, sentences

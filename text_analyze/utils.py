#! coding: utf-8
import re
import string

from lxml.html import diff

from .sentence import Sentence
from .placeholder import PlaceHolder

SENTENCES_END = u'.?!'

SPACE_REGEXP = re.compile('^(\s|&nbsp;)+$', flags=re.I | re.M)


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


def get_sentences(text):
    structure = []
    sentences = []
    sentence = u''
    place_holders = []
    tokens = diff.tokenize(text)

    for position, word_tokens in enumerate(tokens_generator(tokens)):
        word = u''.join(map(unicode, word_tokens))
        word = word.rstrip(SENTENCES_END)

        if word:
            last_token = word_tokens[-1]
            sentence += word + last_token.trailing_whitespace

            place_holder = PlaceHolder(word, position)
            place_holders.append(place_holder)

            structure.append([word_tokens, place_holder])
            if last_token[-1] in SENTENCES_END:
                sentences.append(Sentence(sentence, place_holders))
                sentence = u''
                place_holders = []
        else:
            structure.append([word_tokens, None])
    else:
        if sentence:
            sentences.append(Sentence(sentence, place_holders))
    return structure, sentences

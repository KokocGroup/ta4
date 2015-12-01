from lxml import etree
from lxml.html import fragment_fromstring
import re

try:
    from html import escape as html_escape
except ImportError:
    from cgi import escape as html_escape
try:
    _unicode = unicode
except NameError:
    # Python 3
    _unicode = str
try:
    basestring
except NameError:
    # Python 3
    basestring = str

_body_re = re.compile(r'<body.*?>', re.I | re.S)
_end_body_re = re.compile(r'</body.*?>', re.I | re.S)
_ins_del_re = re.compile(r'</?(ins|del).*?>', re.I | re.S)
end_whitespace_re = re.compile(r'[ \t\n\r]$')


class token(_unicode):
    """ Represents a diffable token, generally a word that is displayed to
    the user.  Opening tags are attached to this token when they are
    adjacent (pre_tags) and closing tags that follow the word
    (post_tags).  Some exceptions occur when there are empty tags
    adjacent to a word, so there may be close tags in pre_tags, or
    open tags in post_tags.

    We also keep track of whether the word was originally followed by
    whitespace, even though we do not want to treat the word as
    equivalent to a similar word that does not have a trailing
    space."""

    # When this is true, the token will be eliminated from the
    # displayed diff if no change has occurred:
    hide_when_equal = False

    def __new__(cls, text, pre_tags=None, post_tags=None, trailing_whitespace=""):
        obj = _unicode.__new__(cls, text)

        if pre_tags is not None:
            obj.pre_tags = pre_tags
        else:
            obj.pre_tags = []

        if post_tags is not None:
            obj.post_tags = post_tags
        else:
            obj.post_tags = []

        obj.trailing_whitespace = trailing_whitespace

        return obj

    def __repr__(self):
        return 'token(%s, %r, %r, %r)' % (_unicode.__repr__(self), self.pre_tags,
                                          self.post_tags, self.trailing_whitespace)

    def html(self):
        return _unicode(self)


class tag_token(token):

    """ Represents a token that is actually a tag.  Currently this is just
    the <img> tag, which takes up visible space just like a word but
    is only represented in a document by a tag.  """

    def __new__(cls, tag, data, html_repr, pre_tags=None,
                post_tags=None, trailing_whitespace=""):
        obj = token.__new__(cls, "%s: %s" % (type, data),
                            pre_tags=pre_tags,
                            post_tags=post_tags,
                            trailing_whitespace=trailing_whitespace)
        obj.tag = tag
        obj.data = data
        obj.html_repr = html_repr
        return obj

    def __repr__(self):
        return 'tag_token(%s, %s, html_repr=%s, post_tags=%r, pre_tags=%r, trailing_whitespace=%r)' % (
            self.tag,
            self.data,
            self.html_repr,
            self.pre_tags,
            self.post_tags,
            self.trailing_whitespace)

    def html(self):
        return self.html_repr


class href_token(token):

    """ Represents the href in an anchor tag.  Unlike other words, we only
    show the href when it changes.  """

    hide_when_equal = True

    def html(self):
        return ' Link: %s' % self


def tokenize(html, include_hrefs=True):
    """
    Parse the given HTML and returns token objects (words with attached tags).

    This parses only the content of a page; anything in the head is
    ignored, and the <head> and <body> elements are themselves
    optional.  The content is then parsed by lxml, which ensures the
    validity of the resulting parsed document (though lxml may make
    incorrect guesses when the markup is particular bad).

    <ins> and <del> tags are also eliminated from the document, as
    that gets confusing.

    If include_hrefs is true, then the href attribute of <a> tags is
    included as a special kind of diffable token."""
    if etree.iselement(html):
        body_el = html
    else:
        body_el = parse_html(html, cleanup=True)
    # Then we split the document into text chunks for each tag, word, and end tag:
    chunks = flatten_el(body_el, skip_tag=True, include_hrefs=include_hrefs)
    # Finally re-joining them into token objects:
    return fixup_chunks(chunks)


def parse_html(html, cleanup=True):
    """
    Parses an HTML fragment, returning an lxml element.  Note that the HTML will be
    wrapped in a <div> tag that was not in the original document.

    If cleanup is true, make sure there's no <head> or <body>, and get
    rid of any <ins> and <del> tags.
    """
    if cleanup:
        # This removes any extra markup or structure like <head>:
        html = cleanup_html(html)
    return fragment_fromstring(html, create_parent=True)


def cleanup_html(html):
    """ This 'cleans' the HTML, meaning that any page structure is removed
    (only the contents of <body> are used, if there is any <body).
    Also <ins> and <del> tags are removed.  """
    match = _body_re.search(html)
    if match:
        html = html[match.end():]
    match = _end_body_re.search(html)
    if match:
        html = html[:match.start()]
    html = _ins_del_re.sub('', html)
    return html


def split_trailing_whitespace(word):
    """
    This function takes a word, such as 'test\n\n' and returns ('test','\n\n')
    """
    stripped_length = len(word.rstrip())
    return word[0:stripped_length], word[stripped_length:]


def fixup_chunks(chunks):
    """
    This function takes a list of chunks and produces a list of tokens.
    """
    tag_accum = []
    cur_word = None
    result = []
    for chunk in chunks:
        if isinstance(chunk, tuple):
            if chunk[0] == 'img':
                src = chunk[1]
                tag, trailing_whitespace = split_trailing_whitespace(chunk[2])
                cur_word = tag_token('img', src, html_repr=tag,
                                     pre_tags=tag_accum,
                                     trailing_whitespace=trailing_whitespace)
                tag_accum = []
                result.append(cur_word)

            elif chunk[0] == 'href':
                href = chunk[1]
                cur_word = href_token(href, pre_tags=tag_accum, trailing_whitespace=" ")
                tag_accum = []
                result.append(cur_word)
            continue

        if is_word(chunk):
            chunk, trailing_whitespace = split_trailing_whitespace(chunk)
            cur_word = token(chunk, pre_tags=tag_accum, trailing_whitespace=trailing_whitespace)
            tag_accum = []
            result.append(cur_word)

        elif is_start_tag(chunk):
            tag_accum.append(chunk)

        elif is_end_tag(chunk):
            if tag_accum:
                tag_accum.append(chunk)
            else:
                cur_word.post_tags.append(chunk)
        else:
            assert(0)

    if not result:
        return [token('', pre_tags=tag_accum)]
    else:
        result[-1].post_tags.extend(tag_accum)

    return result


# All the tags in HTML that don't require end tags:
empty_tags = (
    'param', 'img', 'area', 'br', 'basefont', 'input',
    'base', 'meta', 'link', 'col')

block_level_tags = (
    'address',
    'blockquote',
    'center',
    'dir',
    'div',
    'dl',
    'fieldset',
    'form',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'hr',
    'isindex',
    'menu',
    'noframes',
    'noscript',
    'ol',
    'p',
    'pre',
    'table',
    'ul',
)

block_level_container_tags = (
    'dd',
    'dt',
    'frameset',
    'li',
    'tbody',
    'td',
    'tfoot',
    'th',
    'thead',
    'tr',
)


def flatten_el(el, include_hrefs, skip_tag=False):
    """ Takes an lxml element el, and generates all the text chunks for
    that tag.  Each start tag is a chunk, each word is a chunk, and each
    end tag is a chunk.

    If skip_tag is true, then the outermost container tag is
    not returned (just its contents)."""
    if not skip_tag:
        if el.tag == 'img':
            yield ('img', el.get('src'), start_tag(el))
        else:
            yield start_tag(el)
    if el.tag in empty_tags and not el.text and not len(el) and not el.tail:
        return
    start_words = split_words(el.text)
    for word in start_words:
        yield html_escape(word)
    for child in el:
        for item in flatten_el(child, include_hrefs=include_hrefs):
            yield item
    if el.tag == 'a' and el.get('href') and include_hrefs:
        yield ('href', el.get('href'))
    if not skip_tag:
        yield end_tag(el)
        end_words = split_words(el.tail)
        for word in end_words:
            yield html_escape(word)

split_words_re = re.compile(r'\S+(?:\s+|$)', re.U)


def split_words(text):
    """ Splits some text into words. Includes trailing whitespace
    on each word when appropriate.  """
    if not text:
        return []
    if not text.strip():
        return [text]

    words = split_words_re.findall(text)
    return words

start_whitespace_re = re.compile(r'^[ \t\n\r]')


def start_tag(el):
    """
    The text representation of the start tag for a tag.
    """
    return '<%s%s>' % (
        el.tag, ''.join([' %s="%s"' % (name, html_escape(value, True))
                         for name, value in el.attrib.items()]))


def end_tag(el):
    """ The text representation of an end tag for a tag.  Includes
    trailing whitespace when appropriate.  """
    if el.tail and start_whitespace_re.search(el.tail):
        extra = ' '
    else:
        extra = ''
    return '</%s>%s' % (el.tag, extra)


def is_word(tok):
    return not tok.startswith('<')


def is_end_tag(tok):
    return tok.startswith('</')


def is_start_tag(tok):
    return tok.startswith('<') and not tok.startswith('</')

import re
import unidecode

def camelify(s):
    """
    Simplifies strings into CamelCase strings
    """
    # remove accents
    s = unidecode.unidecode(s)
    s = ''.join(x for x in s.title() if not x.isspace())
    s = s.replace(':', '')
    s = s.replace('.', '')
    return s

def slugify(s):
    """
    Simplifies ugly strings into something URL-friendly.
    >>> print slugify("[Some] _ Article's Title--")
    some-articles-title
    source: https://blog.dolphm.com/slugify-a-string-in-python/
    """

    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    s = s.lower()

    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')

    # "[some]___article's_title__"
    # "some___articles_title__"
    s = re.sub('\W', '', s)

    # "some___articles_title__"
    # "some   articles title  "
    s = s.replace('_', ' ')

    # "some   articles title  "
    # "some articles title "
    s = re.sub('\s+', ' ', s)

    # "some articles title "
    # "some articles title"
    s = s.strip()

    # "some articles title"
    # "some-articles-title"
    s = s.replace(' ', '-')

    # remove accents
    s = unidecode.unidecode(s)

    return s

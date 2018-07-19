import re
import unidecode
import sqlite3 as sql
import json

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

def get_json_data(app):
    with sql.connect(app.config.get('PROTOCOLS_DB')) as con:
        cur = con.cursor()
        cur.execute("SELECT JSON_text FROM Protocols ORDER BY version_id DESC LIMIT 1")
        rows = cur.fetchall()

    if len(rows) == 0 or len(rows[0]) == 0:
        return None

    return json.loads(rows[0][0])

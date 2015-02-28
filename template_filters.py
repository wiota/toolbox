import re
from time import strftime, localtime
from jinja2 import escape
from flask import current_app as app

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def format_date(value):
    return strftime("%b %d %Y", localtime(int(value)))

def format_money(value):
    return "$%.2f" % (value/100.0)

def format_nl2br(value):
    return u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', u'<br>\n') for p in _paragraph_re.split(value))

def bust(url):
    """ Adds a cache buster to the URL. """
    return "%s?v=%s" % (url, app.config["HEROKU_RELEASE_NAME"])

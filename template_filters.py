import re
from time import strftime, localtime

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def format_date(value):
    return strftime("%b %d %Y", localtime(int(value)))

def format_money(value):
    return "$%.2f" % (value/100.0)

def format_nb2br(value):
    return u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(escape(value)))

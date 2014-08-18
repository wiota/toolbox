import os
import requests

def send_email(to, subject, html):
    url = "https://api.mailgun.net/v2/wiota.co/messages"
    auth = ('api', os.environ.get('MAILGUN_API_KEY'))
    payload = {
        "to" : to,
        "from" : "Wiota Co. <goaheadandreply@wiota.co>",
        "subject" : subject,
        "html" : html
    }
    r = requests.post(url, auth=auth, data=payload)

def send_exception(exception, traceback):
    subject = "ERROR: %s" % (exception)
    tb = "<br/>".join(traceback.format_exc().split('\n'))
    tb = tb.replace(' ', '&nbsp;')
    html = "<code style='display:block; font-size: 13px; width:800px'>%s</code>" % tb
    to = ["di@wiota.co", "rh@wiota.co"]
    send_email(to, subject, html)

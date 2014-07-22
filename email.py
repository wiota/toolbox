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

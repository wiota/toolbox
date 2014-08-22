import os
import requests
from jinja2 import Environment, PackageLoader
from premailer import transform


class Email(object):
    url = "https://api.mailgun.net/v2/wiota.co/messages"
    auth = ('api', os.environ.get('MAILGUN_API_KEY'))
    env = Environment(loader=PackageLoader('toolbox.email', 'views'))

    def __init__(self):
        pass

    def send(self):
        self.html = transform(self.html)
        payload = {
            "to" : self.to,
            "from" : "Wiota Co. <goaheadandreply@wiota.co>",
            "subject" : self.subject,
            "html" : self.html
        }
        r = requests.post(self.url, auth=self.auth, data=payload)

class ActionEmail(Email):

    def __init__(self, to, subject, content, link_text, link_href):
        template = self.env.get_template('action.html')
        self.subject = subject
        self.to = to
        self.html = template.render(content=content, link_text=link_text, link_href=link_href)

class AlertEmail(Email):
    pass

class BillingEmail(Email):

    def __init__(self, to, invoice, stripe_event, link):
        date = format_date(invoice.period_start)
        end_date = format_date(invoice.period_end)
        if date != end_date:
            date += " - %s" % end_date
        self.subject = "Wiota Co. - Invoice (%s)" % date
        self.to = to
        self.html = render_template("invoice_created_email.html", e=e)

class ExceptionEmail(Email):

    def __init__(self, exception, traceback):
        self.subject = "ERROR: %s" % (exception)
        tb = "<br/>".join(traceback.split('\n'))
        tb = tb.replace(' ', '&nbsp;')
        self.html = "<code style='display:block; font-size: 13px; width:800px'>%s</code>" % tb
        self.to = ["di@wiota.co", "rh@wiota.co"]
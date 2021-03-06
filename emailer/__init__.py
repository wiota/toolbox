import os
import requests
from jinja2 import Environment, PackageLoader
from premailer import transform
from toolbox.template_filters import format_date, format_money
from flask.ext.login import current_user
from flask import url_for
import json


class Email(object):
    url = "https://api.mailgun.net/v2/wiota.co/messages"
    auth = ('api', os.environ.get('MAILGUN_API_KEY'))
    env = Environment(loader=PackageLoader('toolbox.emailer', 'views'))
    env.filters["money"] = format_money
    env.filters["date"] = format_date

    def __init__(self):
        pass

    def send(self):
        self.html = transform(self.html)
        payload = {
            "to" : self.to,
            "from" : "Wiota Co. <goaheadandreply@wiota.co>",
            "subject" : self.subject,
            "html" : self.html,
            "bcc" : ["di@wiota.co", "rh@wiota.co"]
        }
        r = requests.post(self.url, auth=self.auth, data=payload)

class ActionEmail(Email):

    def __init__(self, to, subject, content, link_text, link_href):
        template = self.env.get_template('action.html')
        self.subject = subject
        self.to = to
        self.html = template.render(content=content, link_text=link_text, link_href=link_href)

class AdminAlertEmail(Email):

    def __init__(self, subject, body):
        self.subject = "[lime][alert] %s" % (subject)
        self.html = body
        self.to = "goaheadandreply@wiota.co"

class BillingEmail(Email):

    def __init__(self, to, invoice, stripe_event, link):
        date = format_date(invoice.period_start)
        end_date = format_date(invoice.period_end)
        if date != end_date:
            date += " - %s" % end_date
        self.subject = "Wiota Co. - Invoice (%s)" % date
        self.to = to
        self.html = render_template("invoice_created_email.html", e=e)

class ReceiptEmail(Email):

    def __init__(self, to, invoice, stripe_event, link):
        self.subject = "Wiota Co. - Receipt (%s)" % format_date(invoice.period_end)
        self.to = to
        template = self.env.get_template('billing.html')
        self.html = template.render(link=link, to=to, invoice=invoice, stripe_event=stripe_event)

class LimeExceptionEmail(Email):

    def __init__(self, exception, traceback):
        self.subject = "[lime][ERROR] %s" % (exception)
        tb = "<br/>".join(traceback.split('\n'))
        tb = tb.replace(' ', '&nbsp;')
        self.html = ""
        self.html = "User was: %s<br/><br/>" % current_user.email
        self.html += "<code style='display:block; font-size: 13px; width:800px'>%s</code>" % tb
        self.to = "goaheadandreply@wiota.co"

class ExceptionEmail(Email):

    def __init__(self, exception, traceback, host, app):
        self.subject = "[%s][ERROR] %s" % (app, exception)
        tb = "<br/>".join(traceback.split('\n'))
        tb = tb.replace(' ', '&nbsp;')
        self.html = "Host was: %s<br/><br/>" % host.hostname
        self.html += "<code style='display:block; font-size: 13px; width:800px'>%s</code>" % tb
        self.to = "goaheadandreply@wiota.co"

# TODO: Deprecated, remove this.
class FacadeExceptionEmail(Email):

    def __init__(self, exception, traceback, host):
        self.subject = "[facade][ERROR] %s" % (exception)
        tb = "<br/>".join(traceback.split('\n'))
        tb = tb.replace(' ', '&nbsp;')
        self.html = "Host was: %s<br/><br/>" % host.hostname
        self.html += "<code style='display:block; font-size: 13px; width:800px'>%s</code>" % tb
        self.to = "goaheadandreply@wiota.co"

class StripeEmail(Email):

    def __init__(self, event):
        mode = "live" if event["livemode"] else "test"
        self.subject = "[lime][stripe-%s] %s" % (mode, event["type"])
        data = json.dumps(event, sort_keys=True, indent=4, separators=(',', ': '))
        data = data.replace('\n','<br />')
        data = data.replace(' ','&nbsp;')
        self.html = "<code style='display:block; font-size: 13px; width:800px'>%s</code>" % (data)
        self.to = "goaheadandreply@wiota.co"

class InviteEmail(ActionEmail):

    def __init__(self, to, link_href):
        subject = "Confirm your new Lime account!"
        content = "Clink the link below to confirm your account:"
        link_text = "Confirm email address"
        super(InviteEmail, self).__init__(to, subject, content, link_text, link_href)

class RegistrationEmail(ActionEmail):

    def __init__(self, to):
        subject = "You've successfully registered."
        content = "Welcome to Lime. To get started, click to login:"
        link_text = "Log in now"
        link_href = url_for("root.index", email=to, _external=True)
        super(RegistrationEmail, self).__init__(to, subject, content, link_text, link_href)

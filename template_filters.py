from time import strftime, localtime

def format_date(value):
    return strftime("%b %d %Y", localtime(int(value)))

def format_money(value):
    return "$%.2f" % (value/100.0)

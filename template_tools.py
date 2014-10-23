from toolbox.models import *
from time import strftime, localtime

def get_category(config, category_name):
    return Category.objects.get(slug=category_name, owner=config["HOST"].owner)

def get_category_by_id(config, id):
    return Category.objects.get(id=id, owner=config["HOST"].owner)

def get_body(config):
    return Body.objects.get(owner=config["HOST"].owner)

def get_page(config, page_name):
    pages = config["HOST"].custom_pages
    return filter(lambda x: x.slug == page_name, pages)[0]

def get_happenings(config):
    return Happenings.objects.get(owner=config["HOST"].owner).succset

def get_tag(config, tag_name):
    return Tag.objects.get(slug=tag_name, owner=config["HOST"].owner).succset

def format_date(value):
    return strftime("%b %d %Y", localtime(int(value)))

def format_money(value):
    return "$%.2f" % (value/100.0)

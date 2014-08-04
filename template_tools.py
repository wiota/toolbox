from toolbox.models import *

def get_category(config, category_name):
    return Category.objects.get(slug=category_name, owner=config["HOST"].owner)

def get_body(config):
    return Body.objects.get(owner=config["HOST"].owner)

def get_page(config, page_name):
    pages = config["HOST"].custom_pages
    return filter(lambda x: x.slug == page_name, pages)[0]

def get_happenings(config):
    return Happening.objects(owner=config["HOST"].owner)

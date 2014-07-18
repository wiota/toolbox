from lime_lib.models import *

def get_category(config, category_name):
    return Category.objects.get(slug=category_name, owner=config["HOST"].owner)

def get_body(config):
    return Body.objects.get(owner=config["HOST"].owner)


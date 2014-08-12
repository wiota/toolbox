from flask.ext.security import UserMixin, RoleMixin, login_required
from mongoengine import *
import bson
import datetime
import re
from mongoengine import signals

# For slugify
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def handler(event):
    """Signal decorator to allow use of callback functions as class decorators."""
    def decorator(fn):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls
        fn.apply = apply
        return fn
    return decorator

@handler(signals.pre_save)
def slugify(sender, document):
    if document.id is None:
        result = []
        for word in _punct_re.split(document.title.lower()):
            word = word.encode('translit/long')
            if word:
                result.append(word)
        slug = slug_attempt = unicode('-'.join(result))
        count = 1
        while sender.objects(**{"slug": slug_attempt, "owner": document.owner}).count() > 0:
            slug_attempt = slug + '-%s' % count
            count += 1
        document.slug = slug_attempt


class LongStringField(StringField):
    pass


class Role(Document, RoleMixin):
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)


class User(Document, UserMixin):
    id = ObjectIdField(
        primary_key=True,
        default=lambda: bson.ObjectId())
    email = EmailField(required=True)
    username = StringField(max_length=50)
    password = StringField()
    admin = BooleanField(default=False)
    stripe_id = StringField()
    confirmed = BooleanField(default=False)
    confirmed_at = DateTimeField()
    registered = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now())
    email_hash = StringField()

    meta = {'allow_inheritance': True}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def activate(self):
        self.confirmed = True
        self.confirmed_at = datetime.datetime.now()
        self.save()

class Sluggable(object):
    slug = StringField(required=True)
    title = StringField(required=True, verbose_name="Title")


@slugify.apply
class CustomPage(EmbeddedDocument, Sluggable):
    template_string = StringField(required=True)
    content = StringField(verbose_name="Content")

class Host(Document):
    bucketname = StringField(required=True)
    owner = ReferenceField(User, required=True)
    custom_pages = ListField(GenericEmbeddedDocumentField(CustomPage))
    hostname = StringField()
    template = StringField()
    title = StringField()
    subtitle = StringField()

    def custom_from_slug(self, slug):
        ret = [cp for cp in self.custom_pages if cp.slug == slug]
        return ret[0] if ret else None

class Client(User):
    hosts = ListField(ReferenceField(Host))


class Administrator(User):
    admin = BooleanField(default=True)


class Vertex(Document):
    _expand_fields = ['succset', 'cover']
    succset = ListField(ReferenceField("self", reverse_delete_rule=PULL))
    predset = ListField(ReferenceField("self", reverse_delete_rule=PULL))
    cover = ListField(ReferenceField("self", reverse_delete_rule=PULL))
    meta = {'allow_inheritance': True}
    owner = ReferenceField(User, required=True)

    def get_save_fields(self):
        return [k for k, v in Category._fields.iteritems() if type(v) is StringField]


class Medium(Vertex):
    pass

class Photo(Medium):
    href = StringField(required=True)


class Video(Medium):
    pass


class Audio(Medium):
    pass


@slugify.apply
class Work(Vertex, Sluggable):
    description = LongStringField(verbose_name="Description")
    date = StringField(verbose_name="Date created")
    medium = StringField(verbose_name="Medium")
    size = StringField(verbose_name="Size")


@slugify.apply
class Category(Vertex, Sluggable):
    pass


@slugify.apply
class Tag(Vertex, Sluggable):
    pass


class Apex(Vertex):
    source = BooleanField(default=True)


class Body(Apex):
    pass


class Happenings(Apex):
    pass


@slugify.apply
class Happening(Vertex, Sluggable):
    description = LongStringField(verbose_name="Description")
    location = StringField(verbose_name="Location")
    link = URLField(verbose_name="Link")
    date_string = StringField(verbose_name="Date string")
    start_date = DateTimeField(verbose_name="Start date")
    end_date = DateTimeField(verbose_name="End date")

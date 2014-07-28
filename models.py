from flask.ext.security import UserMixin, RoleMixin, login_required
from mongoengine import *
import bson
import datetime


class LongStringField(StringField):
    pass


class Role(Document, RoleMixin):
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)


class User(Document, UserMixin):
    _expand_fields = []
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

class CustomPage(EmbeddedDocument):
    slug = StringField(required=True)
    title = StringField(required=True)
    content = StringField(required=True)
    template_string = StringField(required=True)

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
    succset = ListField(ReferenceField("self", reverse_delete_rule=PULL))
    predset = ListField(ReferenceField("self", reverse_delete_rule=PULL))
    cover = ReferenceField("self")
    slug = StringField(required=True)
    title = StringField(required=True, verbose_name="Title")
    meta = {'allow_inheritance': True}
    owner = ReferenceField(User, required=True)

    def get_save_fields(self):
        return [k for k, v in Category._fields.iteritems() if type(v) is StringField]


class Medium(Vertex):
    _expand_fields = []


class Photo(Medium):
    href = StringField(required=True)


class Video(Medium):
    pass


class Audio(Medium):
    pass


class Work(Vertex):
    _expand_fields = ['succset']
    description = LongStringField(verbose_name="Description")
    date = StringField(verbose_name="Date created")
    medium = StringField(verbose_name="Medium")
    size = StringField(verbose_name="Size")


class Category(Vertex):
    _expand_fields = ['succset']


class Tag(Vertex):
    pass


class Body(Vertex):
    _expand_fields = ['succset']
    source = BooleanField(default=True)

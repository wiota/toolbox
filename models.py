from flask_login import UserMixin
from mongoengine import *
import bson


class LongStringField(StringField):
    pass


class User(Document, UserMixin):
    _expand_fields = []
    id = ObjectIdField(
        primary_key=True,
        default=lambda: bson.ObjectId())
    email = EmailField(required=True)
    username = StringField(required=True, max_length=50)
    password = StringField(required=True)
    admin = BooleanField(default=False)
    stripe_id = StringField()

    meta = {'allow_inheritance': True}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


class Host(Document):
    hostname = StringField(required=True)
    bucketname = StringField(required=True)
    owner = ReferenceField(User, required=True)


class Client(User):
    hosts = ListField(ReferenceField(Host))


class Administrator(User):
    admin = BooleanField(default=True)


class Vertex(Document):
    succset = ListField(ReferenceField("self", reverse_delete_rule=PULL))
    predset = ListField(ReferenceField("self", reverse_delete_rule=PULL))
    slug = StringField(required=True)
    title = StringField(required=True, verbose_name="Title")
    meta = {'allow_inheritance': True}
    owner = ReferenceField(User, required=True)


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
    medium = StringField(verbose_name="Medium")
    size = StringField(verbose_name="Size")
    date = StringField(verbose_name="Date created")
    description = LongStringField(verbose_name="Description")


class Category(Vertex):
    _expand_fields = ['succset']


class Tag(Vertex):
    pass


class Body(Vertex):
    _expand_fields = ['succset']
    source = BooleanField(default=True)

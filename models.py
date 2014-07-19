from flask.ext.security import UserMixin, RoleMixin, login_required
from mongoengine import *
from s3 import s3_config
import bson
import datetime
import boto


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

    def build(self):
        # Create the body
        #TODO: Body doesn't need a slug or title
        body = Body(owner=self.id, slug="", title="")
        body.save()

        # Create the S3 stuff
        conn = boto.connect_s3()
        bucket_name ='portphilio_%s' % self.username
        bucket = conn.create_bucket(bucket_name)
        s3_conf = s3_config()
        bucket.set_policy(s3_conf.get_policy(self.username))
        bucket.set_cors_xml(s3_conf.get_cors())

        # Create the host
        # TODO: Where does the hostname get set?
        host = Host(hostname="foo.com", bucketname=bucket_name, owner=self.id)
        host.save


class Host(Document):
    hostname = StringField(required=True)
    bucketname = StringField(required=True)
    owner = ReferenceField(User, required=True)
    template = StringField(required=True)


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

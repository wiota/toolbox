import os
import re
import datetime
import translitcodec
from urlparse import urlparse
from bson.objectid import ObjectId
from bson.dbref import DBRef
from flask import jsonify, request, redirect
from mongoengine.queryset import QuerySet
from mongoengine import Document, StringField, fields
from flask.ext.mongoengine import MongoEngine
from portphilio_lib.models import Subset, Host, Work, LongStringField
import requests
import boto


# For slugify
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def initialize_db(flask_app):
    MONGO_URL = os.environ.get('MONGOHQ_URL')
    flask_app.config["MONGODB_SETTINGS"] = {
        "DB": urlparse(MONGO_URL).path[1:],
        "host": MONGO_URL}
    return MongoEngine(flask_app)


def retrieve_image(image_name, user_name):
    bucket_name = "%s_%s" % (os.environ['S3_BUCKET'], user_name)
    size = request.args.to_dict()
    w = size.get('w', None)
    h = size.get('h', None)
    split = image_name.split(".")
    fn = "".join(split[0:-1])
    ext = split[-1]
    params = {}
    url = "https://%s.s3.amazonaws.com/" % (bucket_name)

    if w is not None or h is not None:  # Some size is given
        fn += "-"  # Separator for size
        if w is not None:
            params["width"] = int(w)
            fn += "%sw" % (w)
        if h is not None:
            params["height"] = int(h)
            fn += "%sh" % (h)

        conn = boto.connect_s3()
        bucket = conn.get_bucket(bucket_name)
        key = bucket.get_key("%s.%s" % (fn, ext))

        if key is None:
            blit_job = {
                "application_id": os.environ['BLITLINE_APPLICATION_ID'],
                "src": {
                    "name": "s3",
                    "bucket": bucket_name,
                    "key": image_name
                },
                "functions": [
                    {
                        "name": "resize_to_fit",
                        "params": params,
                        "save": {
                            "image_identifier": image_name,
                            "s3_destination": {
                                "bucket": bucket_name,
                                "key": "%s.%s" % (fn, ext)
                            },
                        }
                    }
                ]
            }
            r = requests.post(
                "http://api.blitline.com/job",
                data={
                    'json': json.dumps(blit_job)})
        return redirect("%s%s.%s" % (url, fn, ext))
    else:
        return redirect("%s%s" % (url, image_name))


def get_subset(config, subset_name):
    return Subset.objects.get(slug=subset_name, owner=config["OWNER"])


def get_owner(host):
    try:
        return Host.objects.get(hostname=host).owner
    except Host.DoesNotExist:
        return None


def get_work_from_slug(owner, slug):
    work = Work.objects.get(owner=owner, slug=slug)
    return work, work.subset


def bson_encode(obj):
    """Encodes BSON-specific elements to jsonify-able strings"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return unicode(obj)
    elif isinstance(obj, DBRef):
        return unicode(obj.id)
    elif isinstance(obj, list):
        return [bson_encode(x) for x in obj]
    elif not isinstance(obj, dict):
        return obj
    return dict((str(k), bson_encode(v))
                for k, v in obj.items())


def bsonify(*args, **kwargs):
    """ jsonify with support for MongoDB BSON objects
        such as datetime and ObjectId
    """
    ret = bson_encode(kwargs)
    return jsonify(args, **ret)


def to_dict(ret, deref_list=[]):
    """ Converts MongoEngine result to a dict, while dereferencing
        the fields provided
    """
    retdict = ret.to_mongo().to_dict()
    for ref in deref_list:
        if isinstance(ret._data[ref], list):
            retdict[ref] = [x.to_mongo().to_dict() for x in ret._data[ref]]
        else:
            retdict[ref] = ret._data[ref].to_mongo().to_dict()
    return retdict


def make_response(ret=''):
    """ Wraps a dictionary into a response dictionary for the API endpoint to
        return as BSON.
    """
    return {"result": ret}


def slugify(text, delim=u'-'):
    """ Turns any string (e.g., a title) into a URL-able ASCII-only slug.
    """
    result = []
    for word in _punct_re.split(text.lower()):
        word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))


#### MongoEngine Extensions ####


def queryset_to_bson(self):
    """ Converts a QuerySet into a wrapped BSON response.
    """
    return bsonify(**make_response(self.to_dict()))


def queryset_to_dict(self):
    """ Converts the elements in a QuerySet into dictionaries
    """
    return [x.to_dict(expand=False) for x in self]


def document_to_bson(self, expand=True):
    """ Converts a Document into a wrapped BSON response.
    """
    return bsonify(**make_response(self.to_dict(expand)))


def document_to_dict(self, expand=True):
    """ Converts a document into a dictionary, expanding fields as supplied.
    """
    expand_fields = self._expand_fields if expand else []
    return to_dict(self.select_related(), expand_fields)


def document_to_form(self):
    type_dict = {
        StringField.__name__: "text",
        LongStringField.__name__: "textarea"
    }

    ret = {"formFields": {}}
    for field in self._fields:
        if type(self._fields[field]).__name__ in type_dict.keys():
            if self._fields[field].verbose_name is not None:
                ret["formFields"][self._fields[field].name] = {
                    "label": self._fields[field].verbose_name,
                    "required": self._fields[field].required,
                    "type": type_dict[type(self._fields[field]).__name__]}
    return jsonify(ret)


def update_document(document, data_dict):
    """ Updates a MongoEngine document from a dict(). Stolen from:
        http://stackoverflow.com/a/19007761
    """

    def field_value(field, value):

        if field.__class__ in (fields.ListField, fields.SortedListField):
            return [
                field_value(field.field, item)
                for item in value
            ]
        if field.__class__ in (
            fields.EmbeddedDocumentField,
            fields.GenericEmbeddedDocumentField,
            fields.ReferenceField,
            fields.GenericReferenceField
        ):
            return field.document_type(**value)
        else:
            return value

    [setattr(
        document, key,
        field_value(document._fields[key], value)
    ) for key, value in data_dict.items()]

    return document


setattr(QuerySet, 'to_bson', queryset_to_bson)
setattr(QuerySet, 'to_dict', queryset_to_dict)
setattr(Document, 'to_bson', document_to_bson)
setattr(Document, 'to_dict', document_to_dict)
setattr(Document, 'to_form', document_to_form)

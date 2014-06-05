import os
import datetime
from urlparse import urlparse
from bson.objectid import ObjectId
from bson.dbref import DBRef
from flask import jsonify
from mongoengine.queryset import QuerySet
from mongoengine import Document, StringField, fields
from flask.ext.mongoengine import MongoEngine
from portphilio_lib.models import Subset, Host, Work, LongStringField


def initialize_db(flask_app):
    MONGO_URL = os.environ.get('MONGOHQ_URL')
    flask_app.config["MONGODB_SETTINGS"] = {
        "DB": urlparse(MONGO_URL).path[1:],
        "host": MONGO_URL}
    return MongoEngine(flask_app)


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


def make_response(ret):
    """ Wraps a dictionary into a response dictionary for the API endpoint to
        return as BSON.
    """
    return {"result": ret}

#### MongoEngine Extensions ####


def queryset_to_bson(self):
    """ Converts a QuerySet into a wrapped BSON response.
    """
    return bsonify(**make_response(self.to_dict()))


def queryset_to_dict(self):
    """ Converts the elements in a QuerySet into dictionaries
    """
    return [x.to_dict(expand=False) for x in self]


def document_to_bson(self):
    """ Converts a Document into a wrapped BSON response.
    """
    return bsonify(**make_response(self.to_dict()))


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

    ret = {"formFields": []}
    for field in self._fields:
        if type(self._fields[field]).__name__ in type_dict.keys():
            if self._fields[field].verbose_name is not None:
                ret["formFields"].append({self._fields[field].name: {
                    "label": self._fields[field].verbose_name,
                    "required": self._fields[field].required,
                    "type": type_dict[type(self._fields[field]).__name__]}})
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

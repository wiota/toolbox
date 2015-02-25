import os
import datetime
import translitcodec
from operator import itemgetter
from urlparse import urlparse
from bson.objectid import ObjectId
from bson.dbref import DBRef
from flask import g, jsonify, request, redirect, url_for, abort
from mongoengine import Document, fields
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import current_user, AnonymousUserMixin
from toolbox.models import *
from functools import wraps
from itsdangerous import URLSafeSerializer
import requests
import boto
import json


class AnonymousUser(AnonymousUserMixin):

    def __init__(self):
        self.admin = False
        self.email = "(Anonymous User)"


def initialize_db(flask_app):
    MONGO_URL = os.environ.get('MONGOHQ_URL')
    flask_app.config["MONGODB_SETTINGS"] = {
        "DB": urlparse(MONGO_URL).path[1:],
        "host": MONGO_URL}
    return MongoEngine(flask_app)


# Admin view decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            return redirect(url_for("root.index"))
        return f(*args, **kwargs)
    return decorated_function


def retrieve_image(image_name, bucket_name):
    args = request.args.to_dict()
    w = args.get('w', None)
    h = args.get('h', None)
    split = image_name.split(".")
    fn = "".join(split[0:-1])
    ext = split[-1]
    params = {}
    url = "https://%s.s3.amazonaws.com/" % (bucket_name)

    if w is not None or h is not None: # Some size is given
        fn += "-"  # Separator for size
        if w is not None:
            params["width"] = int(w)
            fn += "%sw" % (w)
        if h is not None:
            params["height"] = int(h)
            fn += "%sh" % (h)

        # Allow the blitline function to be passed as a param.
        # The default function is "resize_to_fit"
        function = args.get("function", "resize_to_fit")

        # The "resize_to_fit" function is the default, so to maintain backwards
        # compatibility we don't add it to the filename
        if function is not "resize_to_fit":
            fn += function

        # Connect to the S3 instance
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
                "functions": []
            }
            if ext.lower() == "gif":
                # This image is a gif, to resize we need to preprocess
                blit_job["pre_process"] = {
                    "resize_gif": {
                        "params": params,
                        "s3_destination": {
                            "bucket": bucket_name,
                            "key": "%s.%s" % (fn, ext)
                        }
                    }
                }
                # Since we preprocessed, we don't need to run a function
                blit_job["functions"].append({
                    "name": "no_op",
                    "save": {
                        "image_identifier": image_name
                    }
                })
            else: # This is a regular image
                blit_job["functions"].append({
                    "name": function,
                    "params": params,
                    "save": {
                        "image_identifier": image_name,
                        "save_profiles": "true",
                        "quality": 90,
                        "s3_destination": {
                            "bucket": bucket_name,
                            "key": "%s.%s" % (fn, ext)
                        },
                    }
                })

            # POST the job to blitline
            r = requests.post(
                "http://api.blitline.com/job",
                data={
                    'json': json.dumps(blit_job)})
        return redirect("%s%s.%s" % (url, fn, ext))
    else:
        return redirect("%s%s" % (url, image_name))


def get_host_by_hostname(hostname):
    try:
        return Host.objects.get(hostname=hostname)
    except Host.DoesNotExist:
        return None

def get_body(host):
    return Body.objects.get(host=host)

# May not need these functions...
def get_category_from_slug(host, slug):
    cat = Category.objects.get(host=host, slug=slug)
    return cat

def get_work_from_slug(host, slug):
    work = Work.objects.get(host=host, slug=slug)
    return work

# except this one
def get_happenings_apex(host):
    return Happenings.objects.get(host=host)

def get_happening_from_slug(host, slug):
    happening = Happening.objects.get(host=host, slug=slug)
    return happening

# This function replaces them all
def get_vertex_from_slug(host, slug):
    vertex = Vertex.objects.get(host=host, slug=slug)
    return vertex


def make_response(ret=''):
    """ Wraps a dictionary into a response dictionary for the API endpoint to
        return as BSON.
    """
    return {"result": ret}

def get_custom_vertex_fields(vertex_type):
    # Get the current host
    host = Host.by_current_user()

    # Get any custom fields for the document type
    return host.custom_vertex_fields.get(vertex_type.lower(), [])


def document_to_form(self):
    """ Converts a document into a serialized form. Provides the necessary
        attributes. Use's MongoEngine's `creation_counter` to order the list
        before it is passed as JSON. The type_dict provides a one-to-one
        correspondence between a MongoEngine field and an HTML field type.
    """
    type_dict = {
        StringField.__name__: "text",
        LongStringField.__name__: "textarea",
        DateTimeField.__name__: "datetime-local",
        URLField.__name__: "text"
    }

    # Create a generator containing fields which have a verbose name
    fields = ((v.creation_counter, v)
              for k, v in self._fields.iteritems() if v.verbose_name)

    # Sort the fields based on their creation_counter (first tuple item)
    sorted_fields = map(itemgetter(1), sorted(fields, key=itemgetter(0)))

    # Create the field list object from the sorted fields
    field_list = [{"name": f.name,
                   "label": f.verbose_name,
                   "required": f.required,
                   "type": type_dict[type(f).__name__]} for f in sorted_fields]


    # Add the custom fields to the field list
    for cv in get_custom_vertex_fields(self.__class__.__name__):
        field_list.append({
            "name": cv.name,
            "label": cv.verbose_name,
            "required": cv.required,
            "type": type_dict[cv.field_type]
        })

    return jsonify(make_response(field_list))


def update_document(document, data_dict):
    """ Updates a MongoEngine document from a dict(). Stolen from:
        http://stackoverflow.com/a/19007761
    """

    def field_value(document, key, value):
        """ Get the true value of the field depending on the type. """

        # Support for DynamicDocument types. If the schematic_fields ever
        # become non-regular (e.g., not StringField, BooleanField, etc) then
        # this will become a problem. However, since the type of the
        # schematic_field is stored in the Host, we can just merge it from
        # there before updating the document. But maybe that won't happen...
        if key not in document._fields:
            return value

        # Get the field from the documents's _field array. We've already
        # checked if it's there so it's guaranteed to be
        field = document._fields[key]

        # These are lists, so we should return a list built from recursive
        # calls to field_value
        if field.__class__ in (fields.ListField, fields.SortedListField):
            return [
                field_value(field.field, item)
                for item in value
            ]

        # Here we need to return the proper document_type
        if field.__class__ in (
            fields.EmbeddedDocumentField,
            fields.GenericEmbeddedDocumentField,
            fields.ReferenceField,
            fields.GenericReferenceField
        ):
            return field.document_type(**value)

        # Otherwise, just return the value.
        else:
            return value

    for key, value in data_dict.items():
        setattr(
            document, key,
            field_value(document, key, value)
        )

    return document

setattr(Document, 'to_form', document_to_form)
setattr(EmbeddedDocument, 'to_form', document_to_form)

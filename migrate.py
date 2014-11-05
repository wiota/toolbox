from pymongo import MongoClient
from bson import ObjectId
import argparse
import sys
from boto.s3.connection import S3Connection
from boto.s3.bucket import Bucket
import pprint

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser()
parser.add_argument('--dev-db', help='Development DB URL', required=True)
parser.add_argument('--pro-db', help='Production DB URL', required=True)
parser.add_argument(
    '--dev-owner-id',
    help='Development Owner ID',
    required=True)
parser.add_argument(
    '--pro-owner-id',
    help='Production Owner ID',
    required=True)
parser.add_argument(
    '--aws-access-key-id',
    help='AWS Access Key ID',
    required=True)
parser.add_argument(
    '--aws-secret-access-key',
    help='AWS Secret Access Key',
    required=True)
args = parser.parse_args()


def error(error, e=None):
    if e:
        print "\nERROR: %s: %s\n" % (error, e)
    else:
        print "\nERROR: %s\n" % (error)
    sys.exit(0)


def s3_copy(from_bucket, to_bucket, AWS_ACCESS_KEY, AWS_SECRET_KEY):
    conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
    bucket = Bucket(conn, from_bucket)

    for item in bucket:
        item.copy(to_bucket, item.name)

try:
    dev_client = MongoClient(args.dev_db)
except Exception as e:
    error("Invalid development DB URL param", e)

try:
    pro_client = MongoClient(args.pro_db)
except Exception as e:
    error("Invalid production DB URL param", e)

try:
    dev_owner_id = ObjectId(args.dev_owner_id)
except Exception as e:
    error("Invalid development Owner ID", e)

try:
    pro_owner_id = ObjectId(args.pro_owner_id)
except Exception as e:
    error("Invalid production Owner ID", e)

try:
    dev_db_name = args.dev_db.split('/')[-1]
    dev_db = dev_client[dev_db_name]
except Exception as e:
    error("Dev database '%s' does not exist" % (dev_db_name), e)

try:
    pro_db_name = args.pro_db.split('/')[-1]
    pro_db = pro_client[pro_db_name]
except Exception as e:
    error("Dev database '%s' does not exist" % (pro_db_name), e)

dev_owner = dev_db.user.find_one({"_id": dev_owner_id})
if dev_owner is None:
    error("Development owner not found!")

pro_owner = pro_db.user.find_one({"_id": pro_owner_id})
if pro_owner is None:
    error("Production owner not found!")

dev_vertices = dev_db.vertex.find({"owner": dev_owner_id})
if not dev_vertices.count() > 0:
    error("No vertices to migrate!")

pro_vertices = pro_db.vertex.find({"owner": pro_owner_id})
if pro_vertices.count() > 2:
    error("Non-apex vertices exist in production!")

dev_host = dev_db.host.find({"owner": dev_owner_id})
if dev_host.count() == 0:
    error("No host found in development!")
elif dev_host.count() > 1:
    error("Too many hosts found in development!")

pro_host = pro_db.host.find({"owner": pro_owner_id})
if pro_host.count() == 0:
    error("No host found in production!")
elif pro_host.count() > 1:
    error("Too many hosts found in production!")

dev_host_doc = dev_host.next()
old_pro_host_doc = new_pro_host_doc = pro_host.next()

# These are the host fields that will be modified
new_pro_host_doc['title'] = dev_host_doc['title']
new_pro_host_doc['subtitle'] = dev_host_doc['subtitle']
new_pro_host_doc['custom_vertex_fields'] = dev_host_doc['custom_vertex_fields']
new_pro_host_doc['custom_pages'] = dev_host_doc['custom_pages']

print "\nMigrating %d vertices from:\n\tURL: %s\n\tOwner Email: %s\n\tOwner ID: %s\nto:\n\tURL: %s\n\tOwner Email: %s\n\tOwner ID: %s" % (dev_vertices.count(), args.dev_db, dev_owner["email"], dev_owner_id, args.pro_db, pro_owner["email"], pro_owner_id)

print "\nHost was:"
pp.pprint(old_pro_host_doc)

print "\nHost will become:"
pp.pprint(new_pro_host_doc)

print "\nConfirm migration? (type 'yes')"
if raw_input() != "yes":
    error("Exiting!")

# NOTE: Everything below here happens post-confirmation !!!

print "\nUpdating host document..."
pro_db.host.save(new_pro_host_doc)

print "\nCopying between S3 buckets..."
s3_copy(
    dev_host_doc["bucketname"],
    new_pro_host_doc["bucketname"],
    args.aws_access_key_id,
    args.aws_secret_access_key)

print "\nMigrating vertices..."
# Clear the apex vertices
pro_db.vertex.remove()

for v in dev_vertices:
    # Set the owner to the production user ID
    v["owner"] = pro_owner_id
    pro_db.vertex.save(v)

print "\nMigration finished."

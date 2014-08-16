import os

class s3_config():

    def __init__(self):
        self.policy = '''{
            "Version": "2008-10-17",
            "Id": "Policy1400263641985",
            "Statement": [
                {
                    "Sid": "Stmt1400263639958",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::984987636045:user/portphilio"
                    },
                    "Action": "s3:*",
                    "Resource": "arn:aws:s3:::%(bucket)s_%(email_hash)s/*"
                },
                {
                    "Sid": "AddCannedAcl",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::613648124410:root"
                    },
                    "Action": [
                        "s3:PutObjectAcl",
                        "s3:GetObject",
                        "s3:PutObject"
                    ],
                    "Resource": "arn:aws:s3:::%(bucket)s_%(email_hash)s/*"
                },
                {
                    "Sid": "Stmt1402260824580",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "*"
                    },
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": "arn:aws:s3:::%(bucket)s_%(email_hash)s/*"
                }
            ]
        }'''
        self.cors = '''<?xml version="1.0" encoding="UTF-8"?>
            <CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
                <CORSRule>
                    <AllowedOrigin>*</AllowedOrigin>
                    <AllowedMethod>GET</AllowedMethod>
                    <AllowedMethod>POST</AllowedMethod>
                    <AllowedMethod>PUT</AllowedMethod>
                    <AllowedHeader>*</AllowedHeader>
                </CORSRule>
            </CORSConfiguration>'''

    def get_policy(self, email_hash):
        return self.policy % {'email_hash' : email_hash, 'bucket' : os.environ['S3_BUCKET']}

    def get_cors(self):
        return self.cors

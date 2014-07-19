
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
                        "Resource": "arn:aws:s3:::portphilio_%(username)s/*"
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
                        "Resource": "arn:aws:s3:::portphilio_%(username)s/*"
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
                        "Resource": "arn:aws:s3:::portphilio_%(username)s/*"
                    }
                ]
            }'''
        self.cors = '''<CORSConfiguration>
                <CORSRule>
                    <AllowedOrigin>*</AllowedOrigin>
                    <AllowedMethod>GET</AllowedMethod>
                    <MaxAgeSeconds>3000</MaxAgeSeconds>
                    <AllowedHeader>Authorization</AllowedHeader>
                </CORSRule>
            </CORSConfiguration>'''

    def get_policy(self, username):
        return self.policy % {'username' : username }

    def get_cors(self):
        return self.cors

# scripts

import os

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

def init_aws_bucket(bucket_name, location):
    """
    the purpose of this is to have a single command which can create the sort of 
    bucket (and bucket environment) we will need to get this system working nicely

    """
    # connect to aws using the details provided.
    import boto3 as aws
    import botocore
    from src.scripts import index as scripts
    try:
        # get the env variables to try connecting
        a_id = scripts.get_env_variable('aws_access_key_id')
        a_k = scripts.get_env_variable('aws_secret_access_key')

        # by default, AWS tries to connect using env vars before anything else
        # so see whether that's worked!
        session = aws.session.Session(aws_access_key_id=a_id, aws_secret_access_key=a_k)
        
        s3 = session.resource('s3')
        client = session.client('s3')

        # try create the bucket
        try:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": location})
        except botocore.exceptions.BotoCoreError as e:
            print("Not able to create bucket: "+ str(e))

        f_name = 'test.txt'
        f = open(f_name, 'w')
        f.write("test")
        f.close()
        f = open(f_name, 'rb')
        # check that it's worked by creating and deleting a file
        s3.Bucket(bucket_name).put_object(Key=f_name, Body=f)
        f.close()

        os.unlink(os.getcwd()+'/'+f.name)
        # remove the file, too.
        s3.Object(bucket_name, f_name).delete()

        # now we want to adjust the CORS policy

        res = client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration={
                'CORSRules': [
                    {
                        'AllowedHeaders': [
                            '*',
                        ],
                        'AllowedMethods': [
                            'PUT',
                            'GET',
                            'POST',
                            'HEAD',
                        ],
                        'AllowedOrigins': [
                            '*'
                        ]
                    },
                ]
            },
        )

        # now we want to adjust the ACL
        import json
        bucket_policy = json.dumps({
            "Version": "2012-10-17",
            "Id": "Policy1551859560189",
            "Statement": [
                {
                    "Sid": "Stmt1551859534035",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:PutObject",
                    "Resource": "arn:aws:s3:::"+bucket_name+"/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                },
                {
                    "Sid": "Stmt1551859555020",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:GetObjectAcl"
                    ],
                    "Resource": "arn:aws:s3:::"+bucket_name+"/*"
                }
            ]
        })

        policy_res = client.put_bucket_policy(
            Bucket=bucket_name,
            ConfirmRemoveSelfBucketAccess=False,
            Policy=bucket_policy
        )

    except botocore.exceptions.ClientError as e:
        print("failed to set up your new S3 bucket. "+str(e))
import boto3 #the AWS python HTTP wrapper lib
import botocore

class Aws:
    # define the class which contacts and uses AWS to store data, and retreive
    # resources from

    def __init__(self, bucket_name, profile_name):
        self.bucket_name = bucket_name
        self.profile_name = profile_name
        self.connection = None
        self.client = None

        # this is going to assume you've already done the config work which
        # is normal in any AWS operation (say, with AWSCLI)

        # https://stackoverflow.com/questions/33378422/how-to-choose-an-aws-profile-when-using-boto3-to-connect-to-cloudfront
        boto3.setup_default_session(profile_name=self.profile_name)
        con = boto3.resource('s3')
        self.connection = con
        client = boto3.client('s3')
        self.client = client


    def get_obj(self, key):
        try:
            return self.client.get_object(Bucket=self.bucket_name, Key=key)
        except AttributeError as e:
            print("Failed to get object with key "+key+". Doesn't exist")
            return False
        except self.client.exceptions.NoSuchKey as e:
            print("Failed to get object with key "+key+". Doesn't exist")
            return False

    def get_obj_url(self, key):
        return self.client.generate_presigned_url('get_object', \
        Params={'Bucket': self.bucket_name, 'Key': key})

    def upload_resource(self, resource, type, id):
        if self.aws_exists():
            try:
                data = open(resource, 'rb')
            except IOError:
                print("Resource doesn't exist")
                return False

            # we need to generate a random sequence for the key of the resource
            # fetch the current max

            obj = self.get_obj(id)
            if not obj:
                new_obj = self.connection.Bucket(self.bucket_name).put_object(Key=id, \
                Body=data)
                if not new_obj:
                    print("Resource failed to upload")
                    return False
                else:
                    return id
            else:
                print("Resource found on system already with this ID.")
                return False
        else:
            print("Can't connect to AWS.")
            return False

    def get_all_obj(self):
        # get all the objects in a particular bucket
        objs = []

        if self.aws_exists():
            for b in bucket.objects.all():
                objs.append(b)

            return objs

        else:
            return False

    def rm_objs(self, objs):
        if self.aws_exists():
            # get the bucket!
            bucket = self.connection.Bucket(Bucket=self.bucket_name)

            for key in bucket.objects.all():
                key.delete()


    def aws_exists(self):
        bucket = self.connection.Bucket(self.bucket_name)
        exists = True
        try:
            self.connection.meta.client.head_bucket(Bucket=self.bucket_name)
        except exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False

        return True

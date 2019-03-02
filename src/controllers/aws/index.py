import boto3 #the AWS python HTTP wrapper lib
import botocore
import src.scripts.index as scripts

class Aws:
    # define the class which contacts and uses AWS to store data, and retreive
    # resources from

    def __init__(self, bucket_name, profile_name):
        self.bucket_name = bucket_name
        self.profile_name = profile_name
        self.connection = None
        self.client = None
        self.session = None

        # get the env variables to try connecting
        access_id = scripts.get_env_variable('aws_access_key_id')
        access_key = scripts.get_env_variable('aws_secret_access_key')


        # this is going to assume you've already done the config work which
        # is normal in any AWS operation (say, with AWSCLI)
        # by default, AWS tries to connect using env vars before anything else
        # so see whether that's worked!
        session = boto3.Session( aws_access_key_id=access_id, aws_secret_access_key=access_key)
        con = session.resource('s3')
        client = boto3.client('s3', aws_access_key_id=access_id, aws_secret_access_key=access_key)
        self.connection = con
        self.client = client
        if self.aws_exists():
            # we connected!
            # add the session, because it was right.
            self.session = session
        else:
            # previous failed, cautiously delete conneciton and client
            self.connection = None
            self.client = None
            # if fails to connect, then we need to get the profile vars.
            print("Connecting over profile...")
            try:
                boto3.setup_default_session(profile_name=self.profile_name)
                con = boto3.resource('s3')
                client = boto3.client('s3')

                self.connection = con
                self.client = client
            except botocore.exceptions.ProfileNotFound:
                print("Unable to find profile... unable to connect.")
                return False
                
    def get_obj(self, key):
        try:
            print(self.bucket_name)
            print(key)
            self.client.get_object(Bucket=self.bucket_name, Key=key)
            # triggers an exception if it doesn't exist!

            # useful object is this one, though, because we can apply
            # changes (eg. delete, copy etc.) to it.
            return self.connection.Object(bucket_name=self.bucket_name, key=key)
        except AttributeError as e:
            print("Failed to get object with key "+key+". Doesn't exist")
            return False
        except self.client.exceptions.NoSuchKey as e:
            print("Failed to get object with key "+key+". Doesn't exist")
            return False

    def get_obj_url(self, key):
        return self.client.generate_presigned_url('get_object', \
        Params={'Bucket': self.bucket_name, 'Key': key}, ExpiresIn=129600) #36hrs

    def upload_resource(self, resource, type, id):
        if self.aws_exists():
            try:
                data = open(resource, 'rb')
            except IOError:
                print("Resource doesn't exist")
                return False

            # we need to generate a random sequence for the key of the resource
            # fetch the current max

            # obj = self.connection.Bucket(self)(id)
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
            bucket = self.connection.Bucket(self.bucket_name)
            for b in bucket.objects.all():
                objs.append(b)

            return objs

        else:
            return False

    def rm_objs(self, objs):
        if self.aws_exists():
            # get the bucket!
            bucket = self.connection.Bucket(self.bucket_name)
            print("obj: "+str(objs))
            for obj in objs:
                obj.delete()
            return True
        else:
            return False


    def aws_exists(self):
        bucket = self.connection.Bucket(self.bucket_name)
        try:
            self.connection.meta.client.head_bucket(Bucket=self.bucket_name)
            return True
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False

        return False

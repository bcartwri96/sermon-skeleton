import boto3 #the AWS python HTTP wrapper lib
import botocore
import src.scripts.index as scripts
import urllib.parse

class Aws:
    # define the class which contacts and uses AWS to store data, and retreive
    # resources from

    def __init__(self, bucket_name, profile_name):
        self.bucket_name = bucket_name
        self.profile_name = profile_name
        self.connection = None
        self.client = None
        self.session = None

        try:
            # get the env variables to try connecting
            a_id = scripts.get_env_variable('AWS_ACCESS_KEY_ID')
            a_k = scripts.get_env_variable('AWS_SECRET_ACCESS_KEY')

            # by default, AWS tries to connect using env vars before anything else
            # so see whether that's worked!
            session = boto3.session.Session(aws_access_key_id=a_id, aws_secret_access_key=a_k)
            print(session)
            con = session.resource('s3')
            print(str(con))
            client = session.client('s3')
            print(str(client))
            self.connection = con
            self.client = client
            print(self.aws_exists())
            if self.aws_exists():
                print("Connected over env vars!")
                # we connected!
                # add the session, because it was right.
                self.session = session
                return None # we don't need to do anything else so return
            else:
                print("Failed to connect over env vars.")
                pass #program flow continuing is enough try another method
        except Exception:
                print("failed to fetch the env vars.")
                pass #program flow continuing is enough try another method

        print(self.connection, self.client)
        if not self.connection and not self.client:
            # previous failed, cautiously delete connection and client
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
                if self.aws_exists():
                    print("Connected over profile!")
                else:
                    print("Failed to connect over profile!")
            except botocore.exceptions.ProfileNotFound:
                print("Unable to find profile... unable to connect.")
        

    def get_obj_head(self, key):
        try:
            head = self.client.head_object(Bucket=self.bucket_name, Key=key)
            return head
        except botocore.exceptions.ClientError as e:
            e_code = e.response['Error']['Code']
            if e_code == '403':
                print("Failed to authenticate for item "+str(key))
                return False
            elif e_code == '404':
                print("failed to locate for item "+str(key))
                return False
            else:
                print("failed for unknown reason with key "+str(key))
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

    def get_obj_size(self, key):
        head = self.get_obj_head(key)
        if head:
            return head['ContentLength']
        else:
            return 0

    def get_obj_url(self, key):
        obj = self.client.generate_presigned_url('get_object', \
        Params={'Bucket': self.bucket_name, 'Key': key}, ExpiresIn=129600) #36hrs
        
        # this should be escaped properly inside the AWS Boto3 code, but it wasn't by
        # Amazon engineers, so here I am doing something dodgy. 
        # Attempts were made at using urllib and requests to parse it properly, but I
        # couldn't easily figure out how to correct that, so this simply replaces the
        # offending character with a correct one for HTML.
        obj = obj.replace('&', '&amp;') # this isn't side-effecting for some reason!

        return obj

    def generate_presigned_upload_url(self, name, type):
        from src.controllers.index import find_unique_id, strip_extension
        from flask_login import current_user
        import json

        if self.aws_exists():
            key = find_unique_id(current_user.id) + strip_extension(name)
            print("Key: "+str(key))

            post_url = self.client.generate_presigned_post(Bucket=self.bucket_name, \
            Key=key,Fields = {"acl": "public-read", "Content-Type": type}, \
            Conditions = [{"acl": "public-read"}, {"Content-Type": type}], ExpiresIn=300)

            return json.dumps({'data':post_url, \
            'url': 'https://%s.s3.amazonaws.com/%s' % (self.bucket_name, key), \
            'key': key})

        else:
            return False

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

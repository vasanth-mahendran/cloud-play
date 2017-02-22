# Name: Vasanth Mahendran
# Student ID: 1001246577
# Course number: CSE6331 Spring'2017
# Lab number:

import boto3
import json

BUCKET_NAME = "cloud-s3-vasanth"

# This class implements methods for the user to perform the cloud related services

class play_s3:

    # Constructor to initialize gpg object, generate the key,initialize the swift connection
    # and create the container if not created.
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(BUCKET_NAME)

    # This method list all the files present in the container created
    def list(self):
        files = []
        for file in self.bucket.objects.all():
                files.append(file.key)
        return files

    # This method get the user inputs and upload the encrypted file
    def upload(self, f):
        self.s3.Object(BUCKET_NAME, f.filename).put(Body=f)
        return True

    # This method get the user inputs and download the encrypted file and decrypt it
    def download(self, file_name,version_number):
        return True

    def delete(self, file_name):
        for file in self.bucket.objects.all():
            if file.key == file_name:
                file.delete()
                return True
        return False

    def login(self, user_name,password):
        for file in self.bucket.objects.all():
            if file.key == "users.txt":
                #users_content = file.key.get_contents_as_string()
                print(file)
                res = file.get()["Body"].read().decode("utf-8")
                res_json = json.loads(res)
                for user in res_json['users']:
                    if user['username'] == user_name and user['password'] == password:
                        return True

        return False

    def search(self, keyword):
        return True


# Name: Vasanth Mahendran
# Student ID: 1001246577
# Course number: CSE6331 Spring'2017
# Lab number:

from cloudant.client import Cloudant
from cloudant.query import Query
import datetime
import hashlib

credentials = {
  "username": "9cc9ab8f-6ed9-4f68-8c8c-28c254972ae4-bluemix",
  "password": "8c163b43046e2563384c5f2bdef735b4dc3af94b14033e1b333692046a8db916",
  "host": "9cc9ab8f-6ed9-4f68-8c8c-28c254972ae4-bluemix.cloudant.com",
  "port": 443,
  "url": "https://9cc9ab8f-6ed9-4f68-8c8c-28c254972ae4-bluemix:8c163b43046e2563384c5f2bdef735b4dc3af94b14033e1b333692046a8db916@9cc9ab8f-6ed9-4f68-8c8c-28c254972ae4-bluemix.cloudant.com"
}
DATABASE_NAME = "vasanth"

# This class implements methods for the user to perform the cloud related services


class play_cloudant:

    # Constructor to initialize gpg object, generate the key,initialize the swift connection
    # and create the container if not created.
    def __init__(self):
        self.client = Cloudant(credentials['username'], credentials['password'],url='https://9cc9ab8f-6ed9-4f68-8c8c-28c254972ae4-bluemix.cloudant.com')
        print(self.client)
        self.client.connect()
        self.my_database = self.client[DATABASE_NAME]

    # This method list all the files present in the container created
    def list(self):
        print("-------List files------")
        files = []
        print(self.my_database)
        for document in self.my_database:
            print(document)
            files.append(document)
            print("\n", document['file_name'], "\t", document['version_number'])
        return files

    # This method get the user inputs and upload the encrypted file
    def upload(self, file_data, fn):
        md5Hash = hashlib.md5(file_data.encode('utf-8')).hexdigest()
        query = Query(self.my_database, selector={'file_name': fn})
        docs = query()['docs']
        for doc in docs:
            print('doc--',doc)
        max_vn = 0
        if docs:
            upload = True
            for doc in docs:
                if max_vn < doc['version_number']:
                    max_vn = doc['version_number']
                if doc['hash_value'] == md5Hash:
                    upload = False
            if upload:
                data = {
                    '_id': fn + "_" + str(max_vn+1),
                    'file_name': fn,
                    'version_number': max_vn+1,
                    'last_modified_date': str(datetime.datetime.now()),
                    'contents': file_data,
                    'hash_value': md5Hash
                }
                self.my_database.create_document(data)
                return True
            else:
                print("Content already exist")
                return False
        else:
            data = {
                '_id': fn + "_1",
                'file_name': fn,
                'version_number': 1,
                'last_modified_date': str(datetime.datetime.now()),
                'contents': file_data,
                'hash_value': md5Hash
            }
            print(data)
            self.my_database.create_document(data)
            return True

    # This method get the user inputs and download the encrypted file and decrypt it
    def download(self, file_name,version_number):
        try:
            data = self.my_database[file_name+"_"+str(version_number)]
            return data['contents']
        except Exception as error:
            print("Error while downloading the file", repr(error))
            return ""

    def delete(self, file_name,version_number):
        try:
            data = self.my_database[file_name+"_"+str(version_number)]
            data.delete()
            return True
        except Exception as error:
            print("Error while deleting the file", repr(error))
            return False

play = play_cloudant()
play.client.disconnect()

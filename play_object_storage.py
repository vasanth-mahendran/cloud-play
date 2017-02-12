# Name: Vasanth Mahendran
# Student ID: 1001246577
# Course number: CSE6331 Spring'2017
# Lab number:

import swiftclient
import gnupg
import os

credentials = {
    "auth_url": "https://identity.open.softlayer.com",
    "project": "object_storage_c276b9e5_f0f9_4f74_b1f3_9f4e1e791b98",
    "projectId": "2e366d6fd34946eab77d39ed2dd1f6c7",
    "region": "dallas",
    "userId": "962f9d1715cd428b90ab92af06507a2e",
    "username": "admin_5f87b817d316df514562ffbb17e985a62d472c84",
    "password": "mJ56kbmpdJP)1H,_",
    "domainId": "be7c3c5a9c4542838b462281156eda8e",
    "domainName": "1191947",
    "role": "admin"
}
passphrase = "vasanth"
GNUPG_HOME = '/Users/vasanthmahendran/.gnupg'
GPG_BINARY = '/usr/local/bin/gpg1'
UPLOAD_PATH = '/Users/vasanthmahendran/Downloads/'
UPLOAD_FILE_NAME = 'cloud-play.txt'
CONTAINER_NAME = "vasanth"
MAX_SIZE = 10000000
FILE_MAX_SIZE = 1000000

# This class implements methods for the user to perform the cloud related services


class play_object_storage:

    # Constructor to initialize gpg object, generate the key,initialize the swift connection
    # and create the container if not created.
    def __init__(self):
        self.gpg = gnupg.GPG(gnupghome=GNUPG_HOME, gpgbinary=GPG_BINARY)
        input_data = self.gpg.gen_key_input(key_type="RSA", key_length=1024, passphrase=passphrase)
        self.gpg.gen_key(input_data)
        self.swift_conn = swiftclient.client.Connection(authurl=credentials['auth_url'] + "/v3",
                                                        key=credentials['password'],
                                                        auth_version='3',
                                                        os_options={'project_id': credentials['projectId'],
                                                                    'user_id': credentials['userId'],
                                                                    'region_name': credentials['region']})
        self.swift_conn.put_container(CONTAINER_NAME)
        print('-------Initialized container------')
        self.get_inputs()

    # This method get the inputs from the user and call the appropriate methods to perform
    # the services requested by the user
    def get_inputs(self):
        print("Operations\n1.Store a file\n2.Retrieve a file\n3.List all files\n4.Delete a file\n5.Exit")
        while True:
            op_success = False
            try:
                op_input = int(input('\nEnter choice 1,2,3,4 or 5:'))
            except Exception as error:
                print("Error while getting input", repr(error))
                op_input = 0
            if op_input == 1:
                total_size = self.get_total_size()
                if total_size > MAX_SIZE:
                    print("Size of your cloud container is full!! delete some files to upload new files")
                else:
                    while True:
                        fp_success = False
                        fp_input = input("\nEnter file path (exclude file name and include end slash):")
                        if os.path.isdir(fp_input):
                            while True:
                                fn_success = False
                                fn_input = input("\nEnter file name (include file format as well):")
                                file_path = fp_input + fn_input
                                if os.path.isfile(file_path):
                                    fn_success = True
                                    file_size = os.stat(file_path).st_size
                                    if file_size > FILE_MAX_SIZE:
                                        print("File size exceeds the limit. limit the file size to 1MB")
                                    else:
                                        if total_size + file_size > MAX_SIZE:
                                            print(
                                                "File size exceeds the limit. total size should be less than or equal to 10MB")
                                        else:
                                            with open(file_path, 'rb') as f:
                                                file_data = f.read()
                                                print(file_data)
                                                self.upload(file_data, fn_input)
                                if fn_success:
                                    break
                            fp_success = True
                        else:
                            print("\nFile path does not exist")
                        if fp_success:
                            break
            elif op_input == 2:
                while True:
                    file_input = input("\nEnter file name to download:")
                    if self.download(file_input):
                        break
                    else:
                        print("File name entered is not correct")
            elif op_input == 3:
                self.list()
            elif op_input == 4:
                while True:
                    fd_input = input("\nEnter file name to delete:")
                    self.swift_conn.delete_object(CONTAINER_NAME, fd_input)
                    fd_success = True
                    if fd_success:
                        break
            elif op_input == 5:
                op_success = True
            else:
                print('Invalid option for distance metric')
            if op_success:
                break

    # This method list all the files present in the container created
    def list(self):
        headers, objects = self.swift_conn.get_container(CONTAINER_NAME)
        print("-------List files------", objects)
        list = []
        for obj in objects:
            list.append(obj['name'])
            print("\n", obj['name'])
        return list

    # This method returns the total size of the all the files present in the container
    def get_total_size(self):
        total = 0
        headers, objects = self.swift_conn.get_container(CONTAINER_NAME)
        for obj in objects:
            total = total + obj['bytes']
        return total

    # This method get the user inputs and upload the encrypted file
    def upload(self, file_data, fn):
        file_data_encrypted = self.encrypt(file_data)
        self.swift_conn.put_object(CONTAINER_NAME, fn, file_data_encrypted.data)
        print("-------Upload successful--------")

    # This method get the user inputs and download the encrypted file and decrypt it
    def download(self, file_name):
        try:
            get_data = self.swift_conn.get_object(CONTAINER_NAME, file_name)
            print("-------Download data------")
            print(get_data[1])
            decrypted_data = self.decrypt(get_data[1])
            text_file = open("Output.txt", "w")
            text_file.write("%s" % decrypted_data)
            text_file.close()
            return True
        except Exception as error:
            print("Error while downloading the file", repr(error))
            return False

    # This method encrypt the file using the passphrase and AES algorithm
    def encrypt(self, data):
        return self.gpg.encrypt(data, recipients=None, symmetric='AES256', passphrase=passphrase, armor=False)

    # This method decrypt the file using passphrase
    def decrypt(self, data):
        return self.gpg.decrypt(data, passphrase=passphrase)


play = play_object_storage()
play.swift_conn.close()

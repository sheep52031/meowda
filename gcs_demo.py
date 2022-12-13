import os
from google.cloud import storage

os.environ['GOOGlE_APPLICATION_CREDENTIALS'] = './GCS/ServiceKey_GoogleCloud.json'

storage_client = storage.Client()

print(type(storage_client))

userid = "U3f0ce81f0c841994bffc95b23053c492"

"""
Accessing a Specific Bucket
"""

my_bucket = storage_client.get_bucket('meowda')

print(type(my_bucket))




"""
Upload Files
"""
def upload_to_bucket(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        return True
    except Exception as e:
        print(e)
        return False

file_path = r'C:\Users\Tibame_T14\Desktop\meowda\static\user_cats_photo'
upload_to_bucket(f'user_cats_image/{userid}/17281187502942', os.path.join(file_path, '17281187502942.jpg'), 'meowda')


fileTest = "./static/test.txt"

try:
    os.remove(fileTest)
except OSError as e:
    print(e)
else:
    print("File is deleted successfully")


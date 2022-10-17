import os, json
import boto3
from botocore.exceptions import ClientError
from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
import shutil

## 환경 설정
# read json file
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = '\\'.join([ROOT_DIR, 'config.json'])
static_config_path = '\\'.join([ROOT_DIR, 'static_config.json'])

with open(config_path) as config_file:
    config = json.load(config_file)

with open(static_config_path) as static_config_file:
    static_config = json.load(static_config_file)

# static config key
USERNAME = static_config['share_point']['user']
PASSWORD = static_config['share_point']['password']
AWS_ACCESS_KEY_ID = static_config['aws_bucket']['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = static_config['aws_bucket']['aws_secret_access_key']
BUCKET = static_config['aws_bucket']['bucket_name']
BUCKET_SUBFOLDER = static_config['aws_bucket']['bucket_subfolder'] + config['aws_bucket']['folder']
# non static config key
SHAREPOINT_URL = config['share_point']['url']
SHAREPOINT_SITE = config['share_point']['site']
FOLDER_DIR = config['share_point']['folder_dir']

# 임시 local directory 생성/삭제 func
def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")

def deleteDirectory(directory):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    except OSError:
        print("Error: Failed to delete the directory")

## functions used for aws
    #s3 업로드
def upload_file_to_s3(file_obj, bucket, sub_bucket, file_name):
    file_dir_path = save_file(file_name, file_obj) 
    file_name = sub_bucket+file_name

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    with open(file_dir_path, 'rb') as data:
        try:
            s3_client.upload_fileobj(data, bucket, file_name)
        except ClientError as e:
            print(e)
            data.close()
            return False
        data.close()
    return True
        
    # file 쓰기
def save_file(file_name, file_obj):
    file_dir_path = 'file_write/'+file_name    

    with open(file_dir_path, 'wb') as f:
        f.write(file_obj)
        f.close()
    return file_dir_path

## main
if __name__ == '__main__':
    # sharepoint 폴더 접근
    authcookie = Office365(SHAREPOINT_URL, username=USERNAME, password=PASSWORD).GetCookies()
    site = Site(SHAREPOINT_SITE, version=Version.v365, authcookie=authcookie)
    folder = site.Folder(FOLDER_DIR)
    
    createDirectory('file_write')
    # 해당 folder의 모든 file 탐색
    for ele in folder.files:
        upload_file_to_s3(folder.get_file(ele['Name']), BUCKET, BUCKET_SUBFOLDER, ele['Name'])
    deleteDirectory('file_write')
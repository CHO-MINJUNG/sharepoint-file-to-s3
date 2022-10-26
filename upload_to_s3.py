import os, json
import boto3
import shutil
import pandas as pd

## 환경 설정
# read json file
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = '\\'.join([ROOT_DIR, 'config.json'])
static_config_path = '\\'.join([ROOT_DIR, 'static_config.json'])

with open(config_path, encoding='UTF8') as config_file:
    config = json.load(config_file)
    config = config['aws_bucket']

with open(static_config_path, encoding='UTF8') as static_config_file:
    static_config = json.load(static_config_file)
    static_config = static_config['aws_bucket']

AWS_ACCESS_KEY_ID = static_config['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = static_config['aws_secret_access_key']
BUCKET = static_config['bucket_name']

    
## functions used for aws
    # file 쓰기
def save_file(directory, file_name, file_obj):
    with open(directory+'/'+file_name, 'wb') as f:
        f.write(file_obj)
        f.close()
        
    file_format = file_name.split('.')
    raw_file_name = file_format[0]
    
    xlsx = pd.read_excel(directory+'/'+file_name)
    print(xlsx)
    print(file_name)
    xlsx = xlsx.astype({'gvl_shop_id':'str'})
    xlsx = xlsx.astype({'barcode':'str'})
    xlsx = xlsx.astype({'sale_amt_local':'float'})
    
    print(xlsx.dtypes)
    # xlsx['gvl_shop_id'] = pd.Series(xlsx['gvl_shop_id'], dtype=pd.StringDtype)
    # xlsx['barcode'] = pd.Series(xlsx['barcode'], dtype=pd.StringDtype)

    file_name = raw_file_name+".csv"
    xlsx.to_csv(directory+'/'+file_name, sep=',', index=False)

    return file_name
        
    #s3 업로드
def upload_file_to_s3(file_obj, bucket, sub_bucket, file_name, directory):
    local_file_name = save_file(directory, file_name, file_obj)
    file_name = sub_bucket+local_file_name

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    with open(directory+'/'+local_file_name, 'rb') as data:
        s3_client.upload_fileobj(data, bucket, file_name)
        data.close()
        
def upload_files(folder_obj, BUCKET, sub_bucket, directory):
    for ele in folder_obj.files:
        upload_file_to_s3(folder_obj.get_file(ele['Name']), BUCKET, sub_bucket, ele['Name'], directory)
        
def s3_load(folder_obj, folder_name):
    #환경설정
    directory = "file_write"
    sub_bucket = config['bucket_subfolder'] +"cntry=" + folder_name + "/"
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        if len(folder_obj.files) > 1:
            upload_files(folder_obj, BUCKET, sub_bucket, directory)
        elif len(folder_obj.files) == 1:
            file_name = folder_obj.files[0]['Name']
            upload_file_to_s3(folder_obj.get_file(file_name), BUCKET, sub_bucket, file_name, directory)
    finally:
        if os.path.exists(directory):
            shutil.rmtree(directory)
import os, json
import boto3
import shutil
import pandas as pd
import openpyxl
import win32com.client

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
def save_file(file_dir_path, file_obj):
    with open(file_dir_path, 'wb') as f:  
        f.write(file_obj)
        f.close()
    data = pd.read_excel(file_dir_path, sheet_name='raw data')
    data.to_excel(excel_writer="new_folder/rawdata.xlsx", sheet_name='raw data')
    # excel_file = openpyxl.load_workbook(file_dir_path)
    # for sheet_name in excel_file.get_sheet_names():
    #     new_excel = openpyxl.Workbook()
    #     new_excel.copy_worksheet(excel_file[sheet_name])
    #     new_excel.save(sheet_name+'.csv')
        
# def save_sheet

    #s3 업로드
def upload_file_to_s3(file_obj, bucket, sub_bucket, file_name, directory):
    local_file_dir_path = directory+'/'+file_name    
    save_file(local_file_dir_path, file_obj)
    file_name = sub_bucket+file_name

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    with open(local_file_dir_path, 'rb') as data:
        s3_client.upload_fileobj(data, bucket, file_name)
        data.close()
        
def upload_files(folder_obj, BUCKET, sub_bucket, directory):
    for ele in folder_obj.files:
        upload_file_to_s3(folder_obj.get_file(ele['Name']), BUCKET, sub_bucket, ele['Name'], directory)
        
def s3_load(folder_obj):
    #환경설정
    directory = "file_write"
    sub_bucket = config['bucket_subfolder'] + config['folder']
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        if len(folder_obj.files) > 1:
            upload_files(folder_obj, BUCKET, sub_bucket, directory)
        else:
            file_name = folder_obj.files[0]['Name']
            upload_file_to_s3(folder_obj.get_file(file_name), BUCKET, sub_bucket, file_name, directory)
    finally:
        if os.path.exists(directory):
            shutil.rmtree(directory)
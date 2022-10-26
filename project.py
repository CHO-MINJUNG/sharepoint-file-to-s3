from sharepoint_access import sharepoint_access
from upload_to_s3 import s3_load
import json
import os

def folder_name_recursive(folder_name_list):
    for folder_name in folder_name_list:
        folder = sharepoint_access(folder_name) 
        s3_load(folder, folder_name)

## main
if __name__ == '__main__':
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = '\\'.join([ROOT_DIR, 'config.json'])
    
    with open(config_path, encoding='UTF8') as config_file:
        config = json.load(config_file)
        folder_name_list = config['folder_name']
        
    # sharepoint 폴더 접근
    folder_name_recursive(folder_name_list)
    print("finish")
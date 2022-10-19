from sharepoint_access import sharepoint_access
from upload_to_s3 import s3_load

## main
if __name__ == '__main__':
    # sharepoint 폴더 접근
    folder = sharepoint_access() 
    s3_load(folder)
    print("finish")
import os, json
from shareplum import Site
from shareplum import Office365
from shareplum.site import Version


## 환경 설정
# read json file
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = '\\'.join([ROOT_DIR, 'config.json'])
static_config_path = '\\'.join([ROOT_DIR, 'static_config.json'])

with open(config_path, encoding='UTF8') as config_file:
    config = json.load(config_file)
    config = config['share_point']
with open(static_config_path, encoding='UTF8') as static_config_file:
    static_config = json.load(static_config_file)
    static_config = static_config['share_point']

# static config key
USERNAME = static_config['user']
PASSWORD = static_config['password']

def sharepoint_access(folder_name):
    # 환경설정
    sharepoint_url = config['url']
    sharepoint_site = config['site']
    folder_dir = config['folder_dir']+folder_name
    # sharepoint 폴더 접근
    authcookie = Office365(sharepoint_url, username=USERNAME, password=PASSWORD).GetCookies()
    site = Site(sharepoint_site, version=Version.v365, authcookie=authcookie)
    folder = site.Folder(folder_dir)
    return folder
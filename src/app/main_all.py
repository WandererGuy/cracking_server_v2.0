import requests
from fastapi import FastAPI, HTTPException, Form
from fastapi.staticfiles import StaticFiles
import configparser
import uvicorn
import os 
import sys
import uuid
import requests
from utils.common import fix_path
from routers.model import reply_bad_request, reply_success, reply_server_error
from routers.model import MyHTTPException, my_exception_handler
from utils.common import empty_to_none, empty_to_false

from routers.backend.crack_only_hash import router as crack_only_hash_router
from routers.backend.target_wordlist import router as generate_target_wordlist_router
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir,'static')
config = configparser.ConfigParser()
config_path = os.path.join(current_dir, 'config.ini')
config.read(config_path)
host = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['PORT_ALL'] 
production = config['DEFAULT']['production']
num_workers = int(config['DEFAULT']['num_workers'])




port_status_hash_crack = config['DEFAULT']['port_status_hash_crack']
PORT_BACKEND = config['DEFAULT']['PORT_BACKEND']
port_status_hash_crack = config['DEFAULT']['port_status_hash_crack']
CRACKING_SERVER_PORT_NUM = config['DEFAULT']['CRACKING_SERVER_PORT_NUM']
script_name = 'main_all'
app = FastAPI()
app.mount("/static", StaticFiles(directory=static_path), name="static")
app.add_exception_handler(MyHTTPException, my_exception_handler)

def stage_1():
    url = f"http://{host}:{port_status_hash_crack}/create-session"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    json = response.json()
    session_name = json["result"]["session_name"]
    print ("************* done stage 1: create session *************")
    return session_name

def stage_2(session_name, file_path, file_type):
    print ("************* start stage 2: extract hash from file *************")
    url = f"http://{host}:{CRACKING_SERVER_PORT_NUM}/extract-hash"
    payload = {'file_type': file_type,
    'file_path': file_path,
    'session_name': session_name}
    files=[
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.json()["status_code"] != 200:
        raise MyHTTPException(status_code=response.json()["status_code"] , message=response.json()["message"] )
    url = f"http://{host}:{port_status_hash_crack}/get-status-session"
    payload = {'session_name': session_name}
    files=[
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.json()["status_code"] != 200:
        raise MyHTTPException(status_code=response.json()["status_code"] , message=response.json()["message"] )

    json = response.json()
    session_excel_path = json["result"]["session_excel_path"]
    # print (session_excel_path)

    import pandas as pd
    df = pd.read_excel(session_excel_path, engine='openpyxl')
    hash_value_file = df["hash value in file"][0]
    print(hash_value_file)
    print ("************* done stage 2: extract hash from file, hash saved in", hash_value_file, "*************")
    return hash_value_file, session_excel_path

def stage_3(session_name, hash_value_file, session_excel_path):
    print ("************* start stage 3: find hashcat code for hash in hash file *************")
    url = f"http://{host}:{port_status_hash_crack}/find-code"
    payload = {'hash_file': hash_value_file,
    'session_name': session_name}
    files=[
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.json()["status_code"] != 200:
        raise MyHTTPException(status_code=response.json()["status_code"] , message=response.json()["message"] )

    import pandas as pd
    df = pd.read_excel(session_excel_path, engine='openpyxl')
    hashcat_hash_code = df["hashcat hash code"][0]
    print ("************* done stage 3: find hashcat code for hash in hash file: ", hashcat_hash_code, "*************")
    return hashcat_hash_code


def stage_4(file_path, file_type, targuess_train_result_refined_path):
    # file_path =  r'C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\samples\extract_hash_files\123456789.rar'
    # file_type =  "RAR5"
    session_name = stage_1()
    hash_value_file, session_excel_path = stage_2(session_name=session_name, 
                                                  file_path=file_path, 
                                                  file_type=file_type)
    hashcat_hash_code = stage_3(session_name=session_name, 
                                hash_value_file=hash_value_file, 
                                session_excel_path=session_excel_path)
    print ("************* start stage 4: crack the hash *************")

    url = f"http://{host}:{PORT_BACKEND}/backend-crack-only-hash/"
    payload = {'session_name': session_name,
    'hash_file': hash_value_file,
    'hashcat_hash_code': hashcat_hash_code,
    'additional_wordlist': '',
    'full_name': '',
    'birth': '',
    'email': '',
    'account_name': '',
    'id_num': '',
    'phone': '',
    'other_keywords': '',
    'targuess_train_result_refined_path': targuess_train_result_refined_path}
    files=[

    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    if response.json()["status_code"] != 200:
        raise MyHTTPException(status_code=response.json()["status_code"] , message=response.json()["message"] )

    return response

@app.post("/unlock-archive")
async def unlock_archive(    
    file_path: str = Form(...),
    file_type: str = Form(...),
    targuess_train_result_refined_path : str = Form(...),
):
    return stage_4(file_path=file_path, 
                   file_type=file_type, 
                   targuess_train_result_refined_path = targuess_train_result_refined_path)
    


    
def main():
    print ('INITIALIZING FASTAPI SERVER')
    if empty_to_false(production) == False: 
        uvicorn.run(f"{script_name}:app", host=host, port=int(port_num), reload=True, workers=num_workers)
    else: uvicorn.run(f"{script_name}:app", host=host, port=int(port_num), reload=False, workers=num_workers)


if __name__ == "__main__":
    main()
    
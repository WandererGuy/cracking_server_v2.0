import requests
targuess_train_result_refined_path = 'default'
host = "192.168.1.5"
def stage_1():
    url = f"http://{host}:8011/create-session"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    json = response.json()
    session_name = json["result"]["session_name"]
    print ("************* done stage 1: create session *************")
    return session_name

def stage_2(session_name, file_path, file_type):
    print ("************* start stage 2: extract hash from file *************")
    url = f"http://{host}:8010/extract-hash"
    payload = {'file_type': file_type,
    'file_path': file_path,
    'session_name': session_name}
    files=[
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    url = f"http://{host}:8011/get-status-session"
    payload = {'session_name': session_name}
    files=[
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
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
    url = f"http://{host}:8011/find-code"
    payload = {'hash_file': hash_value_file,
    'session_name': session_name}
    files=[
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    import pandas as pd
    df = pd.read_excel(session_excel_path, engine='openpyxl')
    hashcat_hash_code = df["hashcat hash code"][0]
    print ("************* done stage 3: find hashcat code for hash in hash file: ", hashcat_hash_code, "*************")
    return hashcat_hash_code


if __name__ == "__main__":
    file_path =  r'C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\samples\extract_hash_files\123456789.rar'
    file_type =  "RAR5"
    session_name = stage_1()
    hash_value_file, session_excel_path = stage_2(session_name=session_name, 
                                                  file_path=file_path, 
                                                  file_type=file_type)
    hashcat_hash_code = stage_3(session_name=session_name, 
                                hash_value_file=hash_value_file, 
                                session_excel_path=session_excel_path)

    url = f"http://{host}:8012/backend-crack-only-hash/"
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

    print(response.text)

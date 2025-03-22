import uuid
import os
from routers.model import MyHTTPException
from routers.config import gen_extract_command, support_file_type, hash_type_dict
# change this varibale require change gen_extract_command function too 

# support_file_type = ['BitLocker', '7-Zip', 'WinZip', 'RAR5']

# ls = [0, 22100, 11600, 13600, 13000, 17200, 17210, 17220, 17225, 17230]
# hash_type_dict = {}
# for item in ls:
#     hash_type_dict[str(item)] = item
   

attack_mode_dict = {
    "Straight": 0,
    "Combination": 1,
    "Brute-force": 3,
    "Hybrid Wordlist + Mask": 6,
    "Hybrid Mask + Wordlist": 7,
    "Association": 9
}


def empty_to_none(value):
    return None if value == '' else value

def empty_to_false(value):
    value = value.strip('\n').strip()
    if value in (None, '', 'false', 'False', '0'):
        return False
    elif value in ('true', 'True', '1'):
        return True
        
    return bool(value)

def parse_int(value):
    value = empty_to_none(value)
    try:
        return int(value) if value is not None else None
    except Exception as e:
        message = 'please make sure all numbers are numbers not text '
        raise MyHTTPException(status_code=400, message=message)
 
def check_value_in_dict(value_to_check, dict):
    if value_to_check in dict.keys():
        return True
    else:
        available_keys = ', '.join(map(str, dict.keys()))
        detail=f"{value_to_check} does not exist in the dictionary keys. Available keys: {available_keys}"
        return detail 

def check_value_in_list(value_to_check, ls):
    if value_to_check in ls:
        return True
    else:
        available_keys = ', '.join(map(str, ls))
        detail=f"{value_to_check} does not exist in the dictionary keys. Available keys: {available_keys}"
        return detail 

def list_value_in_dict(support_file_type_list):
        s = ''
        for i in support_file_type_list:
            s += i + ', '
        return s



def data_type_translate(data_name):
    # return hash_type_dict[data_name]
    return data_name
def attack_mode_translate(attack_mode):
    return attack_mode_dict[attack_mode]   
 
# def clean_path (path):
#     # if path != None and path != '':
#     #     path = '/mnt/'+ path
#     #     path = path.replace('D:', 'd').replace('C:','c').replace('E:','e').replace('F:','f').replace('\\', '/')
#     return path

# def refine_hash (hash_type, hash):
    # match hash_type:
    #     case 22100:
    #         command = [
    #             'bitlocker2john',
                
    #         ]
    #         return "Handled case one"
def fix_path (path):     
    path = path.replace('\\\\', '/')   
    return path.replace ('\\', '/')
def generate_unique_filename(UPLOAD_FOLDER, extension="txt"):
    if extension != None:
        filename = f"{uuid.uuid4()}.{extension}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return filename
    else:
        filename = f"{uuid.uuid4()}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return filename 
        
def check_result_available(file):
    with open (file, 'r') as f_:
        f = f_.read()
        if 'Exhausted' in f:
            return False
        else:
            return True
        
def handle_response(response):
    # Check if the response is in JSON format
    if response.status_code == 200:  # Check if the request was successful
        try:
            json_data = response.json()  # Parse the JSON response
            return json_data  # Print the parsed JSON
        except ValueError:
            raise MyHTTPException(status_code=500, message = "send Request to another Backend, have a Response is not valid JSON")
    else:
        raise MyHTTPException(status_code=500, message = f"send Request to another Backend, failed with status code {response.status_code}")
    # sys.exit()

def check_temp(line, TEMP_LIMIT):
    for x in range(TEMP_LIMIT, TEMP_LIMIT+10): # make sure dont miss a temp once over temp limit 
        x = str(x)  
        if f'Temp: {x}c' in line:
            return True
    else: 
        return False


import psutil

def is_file_open(file_path):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for item in proc.open_files():
                if item.path == file_path:
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    return False
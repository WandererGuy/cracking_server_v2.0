import requests
from utils.common import fix_path, handle_response
from routers.model import MyHTTPException
from tqdm import tqdm
import os 
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
def send_hash_crack(url = '', 
                    hash_file = '',
                    wordlist_file = '', 
                    mask_file = '',
                    hashcat_hash_code = '', 
                    attack_mode = '', 
                    rule_path = '', 
                    restore = '',
                    runtime = '',
                    status = '',
                    status_json = '',
                    status_timer = '',
                    gpu_number = '',
                    output_file_name = ''):
    payload = {'hash_file': hash_file,
    'wordlist_file': wordlist_file,
    'mask_file': mask_file,
    'hashcat_hash_code': hashcat_hash_code,
    'attack_mode': attack_mode,
    'rule_path': rule_path,
    'restore': restore,
    'runtime': runtime,
    'status': status,
    'status_json': status_json,
    'status_timer': status_timer,
    'gpu_number': gpu_number,
    'output_file_name': output_file_name}
    files=[]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response



def use_hashcat(hashcat_material: dict, HASH_CRACK_URL):
    # hash_file = 'C:/Users/Admin/CODE/work/PASSWORD_CRACK/cracking_server_v1.0/src/app/static/extract_hash_results/736915d8-d26f-4c19-a45d-2a03503b74e1.txt'
    # wordlist_file = 'C:\\Users\\Admin\\CODE\\work\\PASSWORD_CRACK\\cracking_server_v1.0\\wordlist_samples\\zing_tailieuvn_smallwordlist.txt'
    # hashcat_hash_code = '13000'
    attack_mode = 'Straight'
    status = True
    status_timer = 5
    if "mask_file" in hashcat_material.keys() and "wordlist_file" in hashcat_material.keys():
        raise MyHTTPException(status_code=500, message = "error in use_hashcat argument: mask_file and wordlist_file cannot exist at the same time")
    elif "mask_file" not in hashcat_material.keys() and "wordlist_file" not in hashcat_material.keys():
        raise MyHTTPException(status_code=500, message = "error in use_hashcat argument : either mask_file and wordlist_file must be provided")
    if "mask_file" not in hashcat_material.keys():
        res = send_hash_crack(url = HASH_CRACK_URL,
                                hash_file = hashcat_material['hash_file'],
                                wordlist_file = hashcat_material['wordlist_file'],
                                hashcat_hash_code = hashcat_material['hashcat_hash_code'],
                                attack_mode = attack_mode,
                                rule_path = hashcat_material['rule_path'],
                                status = status,
                                status_timer = status_timer,
                                gpu_number = hashcat_material['gpu_number'], 
                                output_file_name = hashcat_material['output_file_name'])
        return res 

    elif hashcat_material['mask_file'] == None or hashcat_material['mask_file'] == '':
        res = send_hash_crack(url = HASH_CRACK_URL,
                                hash_file = hashcat_material['hash_file'],
                                wordlist_file = hashcat_material['wordlist_file'],
                                hashcat_hash_code = hashcat_material['hashcat_hash_code'],
                                attack_mode = attack_mode,
                                rule_path = hashcat_material['rule_path'],
                                status = status,
                                status_timer = status_timer,
                                gpu_number = hashcat_material['gpu_number'], 
                                output_file_name = hashcat_material['output_file_name'])
        return res 

    if "wordlist_file" not in hashcat_material.keys():
        res = send_hash_crack(url = HASH_CRACK_URL,
                                hash_file = hashcat_material['hash_file'],
                                mask_file = hashcat_material['mask_file'],
                                hashcat_hash_code = hashcat_material['hashcat_hash_code'],
                                attack_mode = attack_mode,
                                rule_path = hashcat_material['rule_path'],
                                status = status,
                                status_timer = status_timer,
                                gpu_number = hashcat_material['gpu_number'], 
                                output_file_name = hashcat_material['output_file_name'])
        return res 

    elif hashcat_material['wordlist_file'] == None or hashcat_material['wordlist_file'] == '':
        res = send_hash_crack(url = HASH_CRACK_URL,
                                hash_file = hashcat_material['hash_file'],
                                mask_file = hashcat_material['mask_file'],
                                hashcat_hash_code = hashcat_material['hashcat_hash_code'],
                                attack_mode = attack_mode,
                                rule_path = hashcat_material['rule_path'],
                                status = status,
                                status_timer = status_timer,
                                gpu_number = hashcat_material['gpu_number'], 
                                output_file_name = hashcat_material['output_file_name'])
        return res 

def handle_hashcat_response(res):
    t = handle_response(res)
    hash_dict = {}
    print ('hashcat response')
    print (t)
    terminate_flag = False

    if t['status_code'] == 200:
        if 'terminate' in t['message'].lower():
            cracked_path = t['result']['path']
            cracked_path = fix_path(cracked_path)
            with open(cracked_path, 'r', encoding = 'utf-8') as f:
                data = f.readlines()
                print ('------------------ CRACKED HASH counting:) ------------------')
                for line in tqdm(data, total = len(data)):

                    line = line.strip('\n').strip()
                    if len(line.split(':')) != 2:
                        continue
                    hash = line.split(':')[0]
                    plaintext = line.split(':')[1]
                    hash_dict[hash] = plaintext
            print ('Done get cracked hash :)')
            progress_phase = t['result']['progress_phase']
            session_name = t['result']['session_name']
            terminate_save = {"terminate_progress_phase":progress_phase,
                              "terminate_session_name":session_name}
            terminate_flag = True
            return hash_dict, terminate_flag, terminate_save

        # if 'hash' not in t['message']:
        # get all crack hash so far (since it add new hash to output file everytime new hash got cracked)
        cracked_path = t['result']['path']
        cracked_path = fix_path(cracked_path)
        with open(cracked_path, 'r', encoding = 'utf-8') as f:
            data = f.readlines()
            for line in data:
                line = line.strip('\n').strip()
                if line == '':  # skip the line at first of file which is empty
                    continue

                hash = line.split(':')[0]
                plaintext = line.split(':')[1]
                hash_dict[hash] = plaintext
        return hash_dict, terminate_flag, None
        # else:
        #     print ('------------------ CRACK HASH SO FAR ------------------')
        #     return None, terminate_flag, None
    else:
        raise MyHTTPException(status_code=t['status_code'], message = t['message'])

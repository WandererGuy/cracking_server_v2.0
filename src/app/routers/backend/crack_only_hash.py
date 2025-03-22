from fastapi import Form, APIRouter
import os 
import uuid
from utils.common import fix_path, handle_response
from routers.model import reply_bad_request, reply_success, MyHTTPException
from routers.config import flow_component
from utils.frontend_validation import is_utf8, target_input_validation, kw_ls_check
from utils.common import empty_to_none, is_file_open
from utils.validate_hashfile import validate_hashfile_request, ls_support_hashcat_hash_code
from utils.backend.targuess import targuess_generate
from utils.backend.hashcat import use_hashcat, handle_hashcat_response
from utils.backend.write_hashfile import write_to_remaining_hashfile, end_cracking, end_cracking_by_terminate
from utils.backend.common import split_file_into_small_big
import time 

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
config_path = os.path.join(parent_dir,'config.ini')

import  shutil
import configparser
config = configparser.ConfigParser()
config.read(config_path)

host_ip = config['DEFAULT']['host'] 
TARGUESS_PORT_NUM = config['DEFAULT']['TARGUESS_PORT_NUM'] 
CRACKING_SERVER_PORT_NUM = config['DEFAULT']['CRACKING_SERVER_PORT_NUM'] 
PORT_BACKEND = config['DEFAULT']['PORT_BACKEND']
HASH_CRACK_URL = f"http://{host_ip}:{CRACKING_SERVER_PORT_NUM}/hash-crack/"
TARGUESS_URL_WORDLIST = f"http://{host_ip}:{TARGUESS_PORT_NUM}/generate-target-wordlist/"
TARGUESS_URL_MASKLIST = f"http://{host_ip}:{TARGUESS_PORT_NUM}/generate-target-mask-list/"
VALIDATE_HASHFILE_URL = f"http://{host_ip}:{CRACKING_SERVER_PORT_NUM}/validate-hashfile/"
MAX_MASK_GENERATE_MASKLIST = int(config['DEFAULT']['MAX_MASK_GENERATE_MASKLIST'])
MAX_MASK_GENERATE_WORDLIST = int(config['DEFAULT']['MAX_MASK_GENERATE_WORDLIST'])
router = APIRouter()
static_path = os.path.join(parent_dir,'static')
hash_dump_folder = os.path.join(static_path,'backend','hash_dump')

backend_temp_output = os.path.join(static_path,'backend_temp_output.txt')
hashcat_temp_output = os.path.join(static_path,'hashcat_temp_output.txt')
backend_temp_step = os.path.join(static_path,'backend_temp_step.txt')
hashcat_cracked_hash_path = os.path.join(static_path, 'cracked_hash')

backend_remaining_hash_path = os.path.join(static_path, 'backend', 'remaining_hash')
backend_cracked_hash_path = os.path.join(static_path, 'backend', 'cracked_hash')

SPEED_CONSTANT = 1
# def constant_adjust_to_speed_crack(speed):
#     test_speed_md5
logging_file = os.path.join(parent_dir, 'logging_exp', 'log.txt')
with open(logging_file, 'w', encoding='utf-8'):
    pass
def write_backend_step(content):
    LOG_FILE = open(logging_file, 'a', encoding='utf-8')
    LOG_FILE.write(content)
    LOG_FILE.write('\n')
    LOG_FILE.close()
    with open(backend_temp_step, 'w', encoding='utf-8') as f:
        f.write(content)
            
from tqdm import tqdm 
def template_output(hashcat_material: dict,
                    uncracked_hashes, 
                    cracked_hashes, 
                    cracked_hash_file, 
                    url_cracked_hash, 
                    remaining_hash_file):

    # continously update cracked and uncracked hashes, cracked hash file is final display output 
    res = use_hashcat(hashcat_material, HASH_CRACK_URL)  
    hash_dict, terminate_flag, terminate_save = handle_hashcat_response(res)
    # hash dict is read from output file, output file is adding up everytime crack hash 
    # even in different process , add at latest cursor 
    # if hash_dict != None:
    print ('collect cracked hashes, collect remaining hashes')

    # Ensure uncracked_hashes is a set for O(1) lookups and removals
    uncracked_hashes = set(uncracked_hashes)
    uncrack_num = len(uncracked_hashes)

    # Use dictionary comprehension to find new cracked hashes
    new_cracked_hashes = {
        key: value for key, value in tqdm(hash_dict.items(), total=len(hash_dict))
        if key in uncracked_hashes
    }

    # Update the existing cracked_hashes with new entries
    cracked_hashes.update(new_cracked_hashes)

    # Remove all newly cracked keys from uncracked_hashes
    uncracked_hashes -= new_cracked_hashes.keys()

    # for key, value in tqdm(hash_dict.items(), total = len(hash_dict)):
    #     if key in uncracked_hashes:
    #         uncracked_hashes.remove(key)
    #         cracked_hashes[key] = value
    LOG_FILE = open(logging_file, 'a', encoding='utf-8')
    LOG_FILE.write(f"cracked {uncrack_num - len(uncracked_hashes)} hashes\n\n\n")
    LOG_FILE.close()
    print ('write remaining hashes to file ')
    write_to_remaining_hashfile(remaining_hash_file, uncracked_hashes)
    
    time.sleep(1)
    with open(remaining_hash_file, 'r') as f:
        if f.read() == "" or f.read() == "\n":
            res = end_cracking(cracked_hashes, cracked_hash_file, url_cracked_hash)
            return res , uncracked_hashes , cracked_hashes

    if uncracked_hashes == []:
        res = end_cracking(cracked_hashes, cracked_hash_file, url_cracked_hash)
        return res , uncracked_hashes , cracked_hashes
    if terminate_flag and terminate_save != None: 
        terminate_progress_phase = terminate_save["terminate_progress_phase"]
        terminate_session_name = terminate_save["terminate_session_name"]
        res = end_cracking_by_terminate(cracked_hashes, cracked_hash_file, url_cracked_hash)
        remaining_hash_file = fix_path(remaining_hash_file)
        res["result"]["path_remain_hash"] = remaining_hash_file
        filename = os.path.basename(remaining_hash_file)
        res["result"]["url_remain_hash"] = f"http://{host_ip}:{PORT_BACKEND}/static/backend/remaining_hash/{filename}"
        res["result"]["terminate_progress_phase"] = terminate_progress_phase
        res["result"]["terminate_session_name"] = terminate_session_name
        time.sleep(5) # saving 
        return res , uncracked_hashes , cracked_hashes
    return None , uncracked_hashes , cracked_hashes
        
@router.post("/backend-crack-only-hash/")
async def backend_crack_only_hash(
    session_name: str = Form(...),
    hash_file: str = Form(...),
    hashcat_hash_code: str = Form(None),
    additional_wordlist: str = Form(None),
    full_name: str = Form(None),
    birth: str = Form(None),
    email: str = Form(None),
    account_name: str = Form(None),
    id_num: str = Form(None),
    phone: str = Form(None),
    other_keywords: str = Form(None),
    targuess_train_result_refined_path: str = Form(...),
    ):
    TARGUESS_TRAIN_RESULT_REFINED_PATH = targuess_train_result_refined_path
    '''
    after each crack method , it takes remaining hash file to be hash file for next process
    '''
    session_folder_path = os.path.join(static_path, 'session', session_name)
    if os.path.exists(session_folder_path) == False:
        message = f"no session name {session_name} does not exist"
        return reply_bad_request(message = message)

    excel_path = os.path.join(session_folder_path, 'session.xlsx')
    message = f'please close excel file {fix_path(excel_path)} so that system can write new data to it'
    if is_file_open(excel_path): return reply_bad_request(message)

    write_backend_step(content= 'VALIDATING USER INPUT')
    url_cracked_hash = f"http://{host_ip}:{PORT_BACKEND}/static/backend/cracked_hash/"

    # can only achieve max mask if all information is provided 
    SMALL_RULE_PATH = os.path.join(os.getcwd(),'samples','rule_sample','clem9669_small.rule')
    BIG_RULE_PATH = os.path.join(os.getcwd(),'samples','rule_sample','OneRuleToRuleThemAll.rule')
    
    SMALL_TRAWLING_WORDLIST = os.path.join(os.getcwd(),'wordlist_samples','ALL_PASSWORD_V2_vn.txt')
    BIG_TRAWLING_WORDLIST = os.path.join(os.getcwd(),'wordlist_samples','zing_tailieuvn_smallwordlist.txt')
    
    LIMIT_SMALL_TARGET_MASK_KEYSPACE = 10**7 # FOR MASK , ABOUT 100 MILLION WORD WORDLIST 
    LIMIT_BIG_TARGET_MASK_KEYSPACE = 10**9# FOR MASK , ABOUT 1 BILLION WORDLIST 
    
    MASKLIST_FILE_TRAWLING = os.path.join(os.getcwd(),'samples','mask','all_Extreme_Breach_Masks_trawling_mask.hcmask')
    # 7 char bruteforce, digit bruteforce 
    FIRST_DESPERATE_MASK = os.path.join(os.getcwd(),'samples','mask','first_desperate.hcmask')
    LIMIT_SMALL_TRAWLING_MASK_KEYSPACE = 10**7 # FOR MASK , ABOUT 100 MILLION WORD WORDLIST 
    LIMIT_BIG_TRAWLING_MASK_KEYSPACE = 10**9# FOR MASK , ABOUT 1 BILLION WORDLIST 


    uncracked_hashes = []
    cracked_hashes = {}
    output_file_name = str(uuid.uuid4()) + '.txt' # hashcat output file in static/cracked_hash
    # this is just final file for output display , everything hashes cracked still update in output file 
    hashcat_cracked_file = os.path.join(hashcat_cracked_hash_path, output_file_name)
    with open (hashcat_cracked_file, 'w') as f:
        f.write('') # to make sure hashcat can write output to smt 
    cracked_hash_file = os.path.join(backend_cracked_hash_path, output_file_name) # also name for backend final output file

    remaining_hash_file = os.path.join(backend_remaining_hash_path, output_file_name) # also name for remain file
    print ('choose remaining hash file: ', remaining_hash_file)
    print ('choose cracked hash file: ', cracked_hash_file)




    if hashcat_hash_code not in ls_support_hashcat_hash_code: 
        return reply_bad_request(message = f"Unsupported hashcat_hash_code '{hashcat_hash_code}' \
                                 . Support hash type: {ls_support_hashcat_hash_code}")
    
    file_info = {
        "hash_file": hash_file,
        "additional_wordlist": additional_wordlist
    }
    target_info = {
        "full_name": full_name,
        "birth": birth,
        "email": email,
        "account_name": account_name,
        "id_num": id_num,
        "phone": phone,
        "other_keywords": other_keywords
    }
    if other_keywords.strip() != '':
        keyword_ls = other_keywords.split(',')
        new_kw_ls = []
        for kw in keyword_ls:
            new_kw_ls.append(kw.replace(' ', ''))
        res, false_kw = kw_ls_check(new_kw_ls)
        if not res:
            return reply_bad_request (f'keyword \'{false_kw}\' must be in same class: all letter, all digit or all special character')

    # standardize input 
    for key, value in file_info.items():
        file_info[key] = empty_to_none(value)
    for key, value in target_info.items():
        target_info[key] = empty_to_none(value)
        if target_info[key] != None:
            is_utf8(target_info[key])

    target_input_validation(target_info)


    if file_info['hash_file'] == None: 
        return reply_bad_request(message = "No hash file input given")
    if not os.path.exists(file_info['hash_file']): 
        return reply_bad_request(message = f"{fix_path(hash_file)} , directory is not found")
    if file_info['additional_wordlist'] != None:
        if not os.path.exists(file_info['additional_wordlist']): 
            return reply_bad_request(message = f"{fix_path(additional_wordlist)} , directory is not found")
    
    print ('------------------ VALIDATING HASH FILE ------------------')
    res = handle_response(validate_hashfile_request(hash_file, 
                      hashcat_hash_code, 
                      hash_dump_folder, 
                      VALIDATE_HASHFILE_URL))
    message = res["message"]
    valid = res["result"]
    if valid == "empty":
        return reply_bad_request(message = 
                        'hash file is empty. \
                        Please add hash to the hash file.')
    if valid == False:
        return reply_bad_request(message = message)
    print ('------------------ hashfile is valid ------------------')

    with open (file_info['hash_file'], 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        for hash in lines:
            hash = hash.strip('\n').strip()
            uncracked_hashes.append(hash)

    uncracked_hashes = list(set(uncracked_hashes))

    shutil.copy(file_info['hash_file'], remaining_hash_file)

    # start working 
    # targuess wordlist
    print ('------------------ GENERATING TARGET WORDLIST ------------------')

    write_backend_step(content = 'GENERATING TARGET WORDLIST')
    res = targuess_generate(targuess_train_result_refined_path = TARGUESS_TRAIN_RESULT_REFINED_PATH,
                            targuess_url = TARGUESS_URL_WORDLIST, 
                            target_info = target_info, 
                            max_mask_generate = MAX_MASK_GENERATE_WORDLIST)
    print ('------------------ receive response from targuess ------------------')
    json_res = handle_response(res)
    WORDLIST_FILE_TARGUESS = fix_path(json_res['result']['path'])
    time.sleep(4) # for targuess SAVE

    if flow_component['target_wl']:
        print ('------------------ ATTEMP WITH TARGET WORDLIST (NO RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH TARGET WORDLIST  (NO RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "wordlist_file": WORDLIST_FILE_TARGUESS,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": '',
            "gpu_number": '', 
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res
    
    if flow_component['target_wl_small_rule']:
        print ('------------------ ATTEMP WITH TARGET WORDLIST (WITH SMALL RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH TARGET WORDLIST  (WITH SMALL RULE)')

        hashcat_material = {
            "hash_file": remaining_hash_file,
            "wordlist_file": WORDLIST_FILE_TARGUESS,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": SMALL_RULE_PATH,
            "gpu_number": '',
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res
    
    if flow_component['small_trawling_wl']:
        print ('------------------ ATTEMP WITH SMALL TRAWLING WORDLIST (NO RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH SMALL TRAWLING WORDLIST  (NO RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "wordlist_file": SMALL_TRAWLING_WORDLIST,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": '',
            "gpu_number": '',
            "output_file_name": output_file_name
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

    if flow_component['small_trawling_wl_small_rule']:
        print ('------------------ ATTEMP WITH SMALL TRAWLING WORDLIST  (WITH SMALL RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH SMALL TRAWLING WORDLIST  (WITH SMALL RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "wordlist_file": SMALL_TRAWLING_WORDLIST,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": SMALL_RULE_PATH,
            "gpu_number": '',
            "output_file_name": output_file_name
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res                                                              

    if flow_component['big_trawling_wl']:
        print ('------------------ ATTEMP WITH BIG TRAWLING WORDLIST (NO RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH BIG TRAWLING WORDLIST  (NO RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "wordlist_file": BIG_TRAWLING_WORDLIST,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": '',
            "gpu_number": '',
            "output_file_name": output_file_name
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

    if flow_component['big_trawling_wl_small_rule']:
        print ('------------------ ATTEMP WITH BIG TRAWLING WORDLIST  (WITH SMALL RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH BIG TRAWLING WORDLIST  (WITH SMALL RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "wordlist_file": BIG_TRAWLING_WORDLIST,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": SMALL_RULE_PATH,
            "gpu_number": '',
            "output_file_name": output_file_name
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res  
    
    print ('------------------ GENERATING TARGET MASKLIST ------------------')
    write_backend_step(content = 'GENERATING TARGUESS MASKLIST')
    res = targuess_generate(targuess_train_result_refined_path = TARGUESS_TRAIN_RESULT_REFINED_PATH,
                            targuess_url = TARGUESS_URL_MASKLIST, 
                            target_info = target_info, 
                            max_mask_generate = MAX_MASK_GENERATE_MASKLIST)
    print ('------------------ receive response from targuess ------------------')
    json_res = handle_response(res)
    time.sleep(4) # for targuess SAVE
    MASKLIST_FILE_TARGUESS = fix_path(json_res['result']['path'])

    MASKLIST_FILE_TARGUESS_SMALL, MASKLIST_FILE_TARGUESS_BIG = split_file_into_small_big(path = MASKLIST_FILE_TARGUESS, 
                                                                                         limit_small_keyspace = LIMIT_SMALL_TARGET_MASK_KEYSPACE, 
                                                                                         limit_big_keyspace = LIMIT_BIG_TARGET_MASK_KEYSPACE)
    time.sleep(4) # for targuess SAVE

    MASKLIST_FILE_TRAWLING_SMALL, MASKLIST_FILE_TRAWLING_BIG = split_file_into_small_big(path = MASKLIST_FILE_TRAWLING, 
                                                                                         limit_small_keyspace = LIMIT_SMALL_TRAWLING_MASK_KEYSPACE, 
                                                                                         limit_big_keyspace = LIMIT_BIG_TRAWLING_MASK_KEYSPACE)
    time.sleep(4) # for SAVE

    if flow_component['small_target_ml']:

        print ('------------------ ATTEMP WITH SMALL TARGET MASKLIST (NO RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH SMALL TARGET MASKLIST (NO RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": MASKLIST_FILE_TARGUESS_SMALL,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": '',
            "gpu_number": '',
            "output_file_name": output_file_name 
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

        print ('------------------ ATTEMP WITH SMALL TARGET MASKLIST (SMALL RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH SMALL TARGET MASKLIST (SMALL RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": MASKLIST_FILE_TARGUESS_SMALL,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": SMALL_RULE_PATH,
            "gpu_number": '', 
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

    if flow_component['big_target_ml']:
        print ('------------------ ATTEMP WITH BIG TARGET MASKLIST (NO RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH BIG TARGET MASKLIST (NO RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": MASKLIST_FILE_TARGUESS_BIG,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": '',
            "gpu_number": '',
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

    if flow_component['big_target_ml_small_rule']:
        print ('------------------ ATTEMP WITH BIG TARGET MASKLIST (SMALL RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH BIG TARGET MASKLIST (SMALL RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": MASKLIST_FILE_TARGUESS_BIG,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": SMALL_RULE_PATH,
            "gpu_number": '',
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res




    if flow_component['small_trawling_ml']:
        print ('------------------ ATTEMP WITH SMALL TRAWLING MASKLIST (NO RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH SMALL TRAWLING MASKLIST (NO RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": MASKLIST_FILE_TRAWLING_SMALL,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": '',
            "gpu_number": '',
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

    if flow_component['small_trawling_ml_small_rule']:
        print ('------------------ ATTEMP WITH SMALL TRAWLING MASKLIST (SMALL RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH SMALL TRAWLING MASKLIST (SMALL RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": MASKLIST_FILE_TRAWLING_SMALL,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": SMALL_RULE_PATH,
            "gpu_number": '',
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

    if flow_component['big_trawling_ml']:
        print ('------------------ ATTEMP WITH BIG TRAWLING MASKLIST (NO RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH BIG TRAWLING MASKLIST (NO RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": MASKLIST_FILE_TRAWLING_BIG,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": '',
            "gpu_number": '',
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

    if flow_component['big_trawling_ml_small_rule']:
        print ('------------------ ATTEMP WITH BIG TRAWLING MASKLIST (SMALL RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH BIG TRAWLING MASKLIST (SMALL RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": MASKLIST_FILE_TRAWLING_BIG,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": SMALL_RULE_PATH,
            "gpu_number": '',
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res


    if flow_component['first_desperate_ml']:
        print ('------------------ ATTEMP WITH FIRST DESPERATE MASKLIST (NO RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH FIRST DESPERATE MASKLIST (NO RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "mask_file": FIRST_DESPERATE_MASK,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": '',
            "gpu_number": '',
            "output_file_name": output_file_name  
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res

    if flow_component['big_trawling_wl_big_rule']:
        print ('------------------ ATTEMP WITH BIG TRAWLING WORDLIST  (WITH BIG RULE) ------------------')
        write_backend_step(content = 'CRACKING HASH WITH BIG TRAWLING WORDLIST  (WITH BIG RULE)')
        hashcat_material = {
            "hash_file": remaining_hash_file,
            "wordlist_file": BIG_TRAWLING_WORDLIST,
            "hashcat_hash_code": hashcat_hash_code,
            "rule_path": BIG_RULE_PATH,
            "gpu_number": '',
            "output_file_name": output_file_name
        }
        res, uncracked_hashes, cracked_hashes = template_output(hashcat_material,
                            uncracked_hashes, 
                            cracked_hashes, 
                            cracked_hash_file, 
                            url_cracked_hash, 
                            remaining_hash_file)
        if res != None: return res  



    if cracked_hashes != {}:
        if uncracked_hashes != []:
            res = end_cracking(cracked_hashes, cracked_hash_file, url_cracked_hash)
            res["message"] = 'End of cracking. Successfully cracked these hashes'
            remaining_hash_file = fix_path(remaining_hash_file)
            res["result"]["path_remain_hash"] = remaining_hash_file
            filename = os.path.basename(remaining_hash_file)
            res["result"]["url_remain_hash"] = f"http://{host_ip}:{PORT_BACKEND}/static/backend/remaining_hash/{filename}"
            return res 
    else:
        return reply_success(message = 'No hash was cracked', result = None)



# @router.post("/resume-session/")
# async def resume_session(
#     terminate_progress_phase: str = Form(...),
#     terminate_session_name: str = Form(...),




#             terminate_save = {"terminate_progress_phase":progress_phase,
#                               "terminate_session_name":session_name}

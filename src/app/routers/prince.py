from fastapi import Form, APIRouter
import os 
import logging
import configparser
import subprocess
import time 
from routers.extract_hash import kill_process
from utils.common import empty_to_none, fix_path, generate_unique_filename, attack_mode_translate, \
                            data_type_translate, check_value_in_dict, check_temp,\
                            attack_mode_dict, hash_type_dict
from utils.prince_hashcat import *
from routers.model import reply_bad_request, reply_success, reply_server_error
from routers.hash_crack import create_hashcat_command_general
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(detail)s', filename='fastapi.log', filemode='w')
# logger = logging.getLogger(__name__)
# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)    
config_path = os.path.join(parent_dir, 'config.ini')
static_path = os.path.join(parent_dir,'static')
prince_run_file = os.path.join(os.path.dirname(parent_dir),'prince','pp64.bin')
cracked_hash_result_folder = os.path.join(static_path,'cracked_hash')
prince_wordlist_folder = os.path.join(static_path,'prince_wordlist_output')

potfile_folder = os.path.join(static_path, "potfiles")
session_folder = os.path.join(parent_dir, "session")
hashcat_temp_output = os.path.join(static_path,'hashcat_temp_output.txt')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
hashcat_running_output = config['DEFAULT']['hashcat_running_output'] 
hashcat_running_output = empty_to_false(hashcat_running_output)
terminal_crack_warmup_time = int(config['DEFAULT']['terminal_crack_warmup_time'])
hashcat_path = os.path.join(os.getcwd(), "hashcat","hashcat.exe")

router = APIRouter()
TEMP_LIMIT = 96
ABORT_SIGNAL = False
COOLDOWN_TIME_GPU = 30

@router.post("/prince-generate/")
async def prince_generate(    
    prince_wordlist: str = Form(...),   # prince wordlist
    keyspace: bool = Form(False),         # Calculate number of combinations
    pw_min: str = Form(None),           # Prstr candidate if length is greater than NUM
    pw_max: str = Form(None),           # Prstr candidate if length is smaller than NUM
    elem_cnt_min: str = Form(None),     # Minimum number of elements per chain
    elem_cnt_max: str = Form(None),     # Maximum number of elements per chain
    wl_dist_len: bool = Form(False),  # Calculate output length distribution from wordlist
    wl_max: str = Form(None),           # Load only NUM words from input wordlist or use 0 to disable
    dupe_check_disable: bool = Form(False), # Disable dupes check for faster initial load
    save_pos_disable: bool = Form(False),   # Save the position for later resume with -s
    skip: str = Form(None),             # Skip NUM passwords from start (for distributed)
    limit: str = Form(None),            # Limit output to NUM passwords (for distributed)
    # output_file: str = Form(None),    # Output-file
    case_permute: bool = Form(False),    # For each word in the wordlist that begins with a letter
                                        # generate a word with the opposite case of the first letter
):
    if not os.path.exists(prince_wordlist):
        message = f"file_path {fix_path(prince_wordlist)} does not exist"
        return reply_bad_request(message = message)

        # Convert empty strings to None for optional parameters
    pw_min = empty_to_none(pw_min)
    pw_max = empty_to_none(pw_max)
    elem_cnt_min = empty_to_none(elem_cnt_min)
    elem_cnt_max = empty_to_none(elem_cnt_max)

    
    wl_max = empty_to_none(wl_max)
    skip = empty_to_none(skip)
    limit = empty_to_none(limit)
    # output_file = empty_to_none(output_file)  # Uncomment if using output_file

    # Handle boolean parameters that may come as empty strings
    keyspace = empty_to_false(keyspace)
    wl_dist_len = empty_to_false(wl_dist_len)
    dupe_check_disable = empty_to_false(dupe_check_disable)
    save_pos_disable = empty_to_false(save_pos_disable)
    case_permute = empty_to_false(case_permute)

    for item in [prince_wordlist]:
        if item != None and os.path.exists(item) is False:
            message = f'file path {fix_path(item)} does not exist'
            return reply_bad_request(message)
    try:
        prince_command = genPrinceCommandNormal(
                        prince_run_file=prince_run_file,
                        prince_wordlist=prince_wordlist,
                        keyspace=keyspace,
                        pw_min=pw_min,
                        pw_max=pw_max,
                        elem_cnt_min=elem_cnt_min,
                        elem_cnt_max=elem_cnt_max,
                        wl_dist_len=wl_dist_len,
                        wl_max=wl_max,
                        dupe_check_disable=dupe_check_disable,
                        save_pos_disable=save_pos_disable,
                        skip=skip,
                        limit=limit,
                        # output_file=output_file,
                        case_permute=case_permute
                        )
        print ('running command')
        print (prince_command)
    except Exception as e:
        return reply_server_error(str(e))
    try:
        filename = generate_unique_filename(prince_wordlist_folder)
        prince_wordlist_file = os.path.join(prince_wordlist_folder,filename)
        prince_command.append('>')
        prince_command.append(prince_wordlist_file)
        process = subprocess.run(' '.join(prince_command),
                                    capture_output=True,
                                    cwd="hashcat",  
                                    shell=True, 
                                    text=True,
                                    encoding = 'utf-8')

        stderr = process.stderr
        if stderr:
            return reply_bad_request(stderr)
        path = f"http://{host_ip}:{port_num}/static/prince_wordlist_output/{filename}"
        message = "Result saved successfully."
        data= reply_success(message, path)
    except Exception as e:
        data= reply_server_error(str(e))
    return data
                            



@router.post("/prince-hashcat/")
async def prince_hashcat(    
    prince_wordlist: str = Form(...),   # prince wordlist
    # keyspace: bool = Form(False),         # Calculate number of combinations
    pw_min: str = Form(None),           # Prstr candidate if length is greater than NUM
    pw_max: str = Form(None),           # Prstr candidate if length is smaller than NUM
    elem_cnt_min: str = Form(None),     # Minimum number of elements per chain
    elem_cnt_max: str = Form(None),     # Maximum number of elements per chain
    # wl_dist_len: bool = Form(False),  # Calculate output length distribution from wordlist
    wl_max: str = Form(None),           # Load only NUM words from input wordlist or use 0 to disable
    dupe_check_disable: bool = Form(False), # Disable dupes check for faster initial load
    save_pos_disable: bool = Form(False),   # Save the position for later resume with -s
    skip: str = Form(None),             # Skip NUM passwords from start (for distributed)
    limit: str = Form(...),            # Limit output to NUM passwords (for distributed)
    # output_file: str = Form(None),    # Output-file
    case_permute: bool = Form(False),    # For each word in the wordlist that begins with a letter
                                        # generate a word with the opposite case of the first letter
    hash_file: str = Form(...), 
    hashcat_hash_code: str = Form(...),
    attack_mode: str = Form(None),
    rule_path: str = Form(None),
    restore: str = Form(None),
    runtime: str = Form(None),
    status: str = Form(None),
    status_json: str = Form(None),
    status_timer: str = Form(None),
    gpu_number: str = Form(None)

):
    hash_type = hashcat_hash_code
    mask_file = None
    wordlist_file = None
                ################## PRINCE ##################
    # Handle integer parameters that may come as empty strings
    pw_min = parse_int(pw_min)
    pw_max = parse_int(pw_max)
    elem_cnt_min = parse_int(elem_cnt_min)
    elem_cnt_max = parse_int(elem_cnt_max)
    wl_max = parse_int(wl_max)
    skip = parse_int(skip)
    limit = parse_int(limit)  # Since limit is required, ensure it's an integer
    # Handle boolean parameters that may come as empty strings
    dupe_check_disable = empty_to_false(dupe_check_disable)
    save_pos_disable = empty_to_false(save_pos_disable)
    case_permute = empty_to_false(case_permute)

    if not os.path.exists(prince_wordlist):
        message = f"file_path {fix_path(prince_wordlist)} does not exist"
        return reply_bad_request(message = message)

                ################## HASHCAT ##################
    attack_mode = empty_to_none(attack_mode)
    rule_path = empty_to_none(rule_path)
    restore = empty_to_none(restore)
    runtime = empty_to_none(runtime)
    status = empty_to_none(status)
    status_json = empty_to_none(status_json)
    status_timer = empty_to_none(status_timer)
    gpu_number = empty_to_none(gpu_number)

    for item in [hash_file, rule_path]:
        if item != None and os.path.exists(item) is False:
            message = f'file path {fix_path(item)} does not exist'
            return reply_bad_request (message)
        
    if status in ["True", "1", "true"]:
        status = "True"

    for item in [hash_file, rule_path]:
        if item != None and os.path.exists(item) is False:
            message = f'file path {fix_path(item)} does not exist'
            return reply_bad_request (message)

    if attack_mode == None:
        message = "please provide attack_mode"
        return reply_bad_request (message)
    
    potfile_name = generate_unique_filename(potfile_folder , extension="txt")
    potfile_path = os.path.join(potfile_folder, potfile_name)
    output_file_name = generate_unique_filename(cracked_hash_result_folder , extension="txt")
    output_file = os.path.join(cracked_hash_result_folder, output_file_name)

                ################## PRINCE ##################
    try:
        prince_command = genPrinceCommandHashcat(
                        prince_run_file=prince_run_file,
                        prince_wordlist=prince_wordlist,
                        # keyspace=keyspace,
                        pw_min=pw_min,
                        pw_max=pw_max,
                        elem_cnt_min=elem_cnt_min,
                        elem_cnt_max=elem_cnt_max,
                        # wl_dist_len=wl_dist_len,
                        wl_max=wl_max,
                        dupe_check_disable=dupe_check_disable,
                        save_pos_disable=save_pos_disable,
                        skip=skip,
                        limit=limit,
                        case_permute=case_permute
                        )
    except Exception as e:
       return reply_server_error(str(e))

    try:
        # Check if the value exists in the dictionary keys
        detail = check_value_in_dict(attack_mode, attack_mode_dict)
        if detail is not True:
            return reply_bad_request(message = detail)
        detail = check_value_in_dict(hash_type, hash_type_dict)     
        if detail is not True:
            return reply_bad_request(message = detail)
        hash_type = str(data_type_translate(hash_type))
        attack_mode = str(attack_mode_translate(attack_mode))

        # Build the Hashcat command
        hashcat_input_dict = {
        "hash_file": hash_file,
        "mask_file": mask_file,
        "wordlist_file": wordlist_file,
        "hash_type": hash_type,
        "attack_mode": attack_mode,
        "rule_path": rule_path,
        # "session_name": session_name,
        "restore": restore,
        "output_file": output_file,
        "runtime": runtime,
        "potfile_path": potfile_path,
        "status": status,
        "status_json": status_json,
        "status_timer": status_timer,
        "gpu_number": gpu_number
    }
        if hashcat_running_output: text = True
        else: text = False

        command = create_hashcat_command_general(hashcat_input_dict)
        cm = " ".join(command)
        print ('-------------------') 
        print (command)
        print('')
        print (cm)   
        session_name = str(uuid.uuid4())
        command.append('--session')
        command.append(session_name)
        command[0] = hashcat_path

        ####### PRINCE PIPE #######
        prince_command.append('|')
        full_command = prince_command
        for i in command:
            full_command.append(i)
        cm = " ".join(full_command)
        print ('-------------------') 
        print (full_command)
        print('')
        print (cm)   
        RESTORE = True
        first_flag = True
        exhausted_flag = False

        # piping '|'require shell feature so shell = True 
        if hashcat_running_output: text = True
        else: text = False
        while RESTORE: # until no more restore due to heat 
                if first_flag == False:
                        print (f'cooling gpu for {COOLDOWN_TIME_GPU} seconds')
                        time.sleep(COOLDOWN_TIME_GPU) # 
                        print ('------------- REBORN SESSION --------------')
                        command = [hashcat_path, '--session', session_name, '--restore']
                else:
                        first_flag = False
                        RESTORE = False
                process = subprocess.Popen(full_command, 
                                    cwd="hashcat", 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=text, 
                                    shell=True,
                                    encoding='utf-8') 
                # Read and print output line by line as it comes
                time.sleep(terminal_crack_warmup_time)
                flag = False
                for line in process.stdout:
                    if ": Exhausted" in line: 
                        RESTORE = False # escape hashcat , no more reborn 
                        exhausted_flag = True
                    elif ": Cracked" in line: 
                        RESTORE = False # escape hashcat , no more reborn
                    if ABORT_SIGNAL == False:
                        if 'Temp:' in line and 'Fan' in line:
                            last_temp = line.split('Fan')[0].split('Temp: ')[1]
                            ABORT_SIGNAL = check_temp(line, TEMP_LIMIT)
                            print ('ABORT_SIGNAL: ', ABORT_SIGNAL)
                    if "Session..........: " in line:
                        tmp = []
                        flag = True
                    if "Hardware.Mon." in line:
                        tmp.append(line)
                        flag = False
                        with open (hashcat_temp_output, 'w', encoding='utf-8', errors='ignore') as f:
                            for line in tmp:
                                f.write(line)
                    if flag:
                        tmp.append(line)
                    if hashcat_running_output: print(line, end='')  # Print the output in real-time
                    if ABORT_SIGNAL == True and ' [q]uit' in line: # kill after take the last restore 
                        print('OVERHEAT...ABORTING PROCESS..............')
                        print ('last temp recorded: ', last_temp)
                        RESTORE = True # if die due to heat , reborn
                        ABORT_SIGNAL = False
                        kill_process(process)     
                        break  # Exit the loop after terminating

        # Optionally, handle stderr (error output)
        _, stderr = process.communicate()
        if stderr:
            if "No hashes loaded" in stderr:
                message = "No hash found in file OR hashcat_hash_code is not correct with hash in file"
                reply_bad_request(message=message)
            else:
                reply_bad_request(message=stderr)
        kill_process(process)




        url_output = f"http://{host_ip}:{port_num}/static/cracked_hash/{output_file_name}"
        ### check for result 
        output_file_path = os.path.join(cracked_hash_result_folder, output_file)
        if not os.path.exists(output_file_path):
            message = "Wordlist Exhausted. Cannot crack ANY hash. Maybe find more wordlists"
            return reply_success(message = message,
                                        result = None)
                
        with open (output_file_path, 'r') as f:
            cracked_data_lines = f.readlines()
        with open (output_file_path, 'r') as f: 
            with open (hash_file, 'r') as hf:
                hf_data = hf.readlines()
                miss = 0 
                for item in hf_data:
                    if item.strip().strip('\n').strip('\t') == "":
                        miss += 1 
            if len(cracked_data_lines) < len(hf_data) - miss:
                message = f"cracked {len(cracked_data_lines)} over {len(hf_data)} hashes"
                return reply_success(message = message,
                                    result = {"path": os.path.join(cracked_hash_result_folder, output_file_name),
                                            "url": url_output})
        message = "Sucessfully crack all hashes"
        return reply_success(message = message,
                            result = {"path": os.path.join(cracked_hash_result_folder, output_file_name),
                                      "url": url_output})

    except Exception as e:
        return reply_server_error(e)
    #     stderr = process.stderr

    #     if stderr:
    #         message = str(stderr)
    #         return reply_bad_request(message)


    #     # Giao tiếp với tiến trình con
    #     full_command.append('--show')
    #     process = subprocess.run(' '.join(full_command),
    #                                 capture_output=True,
    #                                 cwd="hashcat",  
    #                                 shell=True, 
    #                                 text=True,
    #                                 encoding = 'utf-8')

    #     stderr = process.stderr
    #     stdout = process.stdout
    
    #     if stderr:
    #         message = str(stderr)
    #         return reply_bad_request(message)

    #     if stdout == '' or stdout == None:
    #         message = "Wordlist Exhausted. Cannot crack hash. Maybe find more wordlists"
    #         return reply_success(message, None)

    #     with open(cracked_hash_result_file, 'w') as f:
    #         f.writelines(stdout)
    #     with open(crack_collection, 'a') as f:
    #         f.writelines(stdout)
    #     # crack_collection_url = crack_collection.split("static",1)[1]
    #     # crack_collection_url = '/static' + crack_collection_url
    #     url = f"http://{host_ip}:{port_num}/static/cracked_hash/{filename}"
    #     # bonus_path = f"http://{host_ip}:{port_num}{crack_collection_url}" # potfile path
    #     message = "Result saved successfully"
    #     return reply_success(message = message, 
    #                          result = {"path":os.path.join(cracked_hash_result_folder, filename),
    #                                    "url":url})

    # except Exception as e:
    #     return reply_server_error(e)

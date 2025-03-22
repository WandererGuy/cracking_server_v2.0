import subprocess
import threading
import time
from fastapi import Form, APIRouter
import os 
import configparser
import subprocess
from utils.common import empty_to_none, fix_path, generate_unique_filename, attack_mode_translate, \
                            data_type_translate, check_value_in_dict, check_temp,\
                            attack_mode_dict, hash_type_dict
from routers.model import reply_bad_request, reply_success, reply_server_error
from utils.common import empty_to_false
import uuid
from routers.extract_hash import kill_process
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
config_path = os.path.join(parent_dir,'config.ini')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
terminal_crack_warmup_time = int(config['DEFAULT']['terminal_crack_warmup_time'])
hashcat_running_output = config['DEFAULT']['hashcat_running_output'] 
hashcat_running_output = empty_to_false(hashcat_running_output)
# Construct the path to config.ini
static_path = os.path.join(parent_dir,'static')
crack_collection = os.path.join(static_path, "potfiles", "potfile.txt")
session_folder = os.path.join(static_path, "session")
cracked_hash_result_folder = os.path.join(static_path, 'cracked_hash')
potfile_folder = os.path.join(static_path, "potfiles")
hashcat_temp_output = os.path.join(static_path,'hashcat_temp_output.txt')
hashcat_path = os.path.join(os.getcwd(), "hashcat","hashcat.exe")
hashcat_terminate_file = os.path.join(static_path,'hashcat_terminate_file.txt')
backend_temp_output = os.path.join(static_path,'backend_temp_output.txt')
current_dir = os.path.dirname(os.path.abspath(__file__))
TEMP_LIMIT = 96
ABORT_SIGNAL = False
COOLDOWN_TIME_GPU = 30
def create_hashcat_command_general(input: dict):
    command = ["hashcat"]
    check_dict = {
        "hash_file": input.get("hash_file", None),
        "mask_file": input.get("mask_file", None),
        "wordlist_file": input.get("wordlist_file", None),
        "hash_type": input.get("hash_type", None),
        "attack_mode": input.get("attack_mode", None),
        "rule_path": input.get("rule_path", None),
        "session_name": input.get("session_name", None),
        "restore": input.get("restore", None),
        "output_file": input.get("output_file", None),
        "runtime": input.get("runtime", None),
        "potfile_path": input.get("potfile_path", None),
        "status": input.get("status", None),
        "status_json": input.get("status_json", None),
        "status_timer": input.get("status_timer", None),
        "increment": input.get("increment", None),
        "increment_min": input.get("increment_min", None),
        "gpu_number": input.get("gpu_number", None),
    }
    # Create the command structure
    trigger_dict = {
            "hash_type": '-m',
            "attack_mode": '-a',
            "rule_path": '-r',
            # "session_name": '--session',
            "output_file": '-o',
            "runtime": '--runtime',
            "potfile_path": "--potfile-path",
            "status": "--status",
            "status_json": "--status-json",
            "status_timer": "--status-timer",
            "increment": "--increment",
            "increment_min": "--increment-min",
            "gpu_number": "-d"
        }
    non_value_ls = ["increment"]
    for key, value in check_dict.items():
        if value != None:
            if key in trigger_dict:
                command.append(trigger_dict[key])
                
            if key not in non_value_ls :
                if key != "status": # since hashcat enable timer by not having value for status
                    command.append(value)
    # command.append('--hwmon-temp-abort=85')
    return command



router = APIRouter()
@router.post("/hash-crack/")
async def hash_crack(  
    hash_file: str = Form(...),
    mask_file: str = Form(None),
    wordlist_file: str = Form(None),
    hashcat_hash_code: str = Form(...),
    attack_mode: str = Form(None),
    rule_path: str = Form(None),
    restore: str = Form(None),
    runtime: str = Form(None),
    status: str = Form(None),
    status_json: str = Form(None),
    status_timer: str = Form(None),
    gpu_number: str = Form(None),
    output_file_name: str = Form(...)
):
    global ABORT_SIGNAL
    hash_type = hashcat_hash_code
    mask_file = empty_to_none(mask_file)
    wordlist_file = empty_to_none(wordlist_file)
    attack_mode = empty_to_none(attack_mode)
    rule_path = empty_to_none(rule_path)
    restore = empty_to_none(restore)
    runtime = empty_to_none(runtime)
    status = empty_to_none(status)
    status_json = empty_to_none(status_json)
    status_timer = empty_to_none(status_timer)
    gpu_number = empty_to_none(gpu_number)

    if status in ["True", "1", "true"]:
        status = "True"
    with open(hashcat_terminate_file, 'w') as f:
        f.write("")


    for item in [hash_file, mask_file, wordlist_file, rule_path]:
        if item != None and os.path.exists(item) is False:
            message = f'file path {fix_path(item)} does not exist'
            return reply_bad_request (message)

    if mask_file != None and wordlist_file != None:
        message = "please only provide 1 wordlist or 1 masklist"
        return reply_bad_request (message)
    if attack_mode == None:
        message = "please provide attack_mode"
        return reply_bad_request (message)
    potfile_name = generate_unique_filename(potfile_folder , extension="txt")
    potfile_path = os.path.join(potfile_folder, potfile_name)
    output_file = os.path.join(cracked_hash_result_folder, output_file_name)
    if os.path.exists(output_file):
        need_move_new_line = False
        with open(output_file, 'r') as f:
            content = f.read()
            if content != "":
                need_move_new_line = True
        if need_move_new_line:
            with open(output_file, 'a') as f:
                f.write('\n')
                
    """
    Hashcat crack given hash using wordlist/masklist. <br>
    Input:<br>
        hash_type : type of the hash<br>
        wordlist : wordlist path / masklist path<br>
        attack_mode : attacking mode <br>

    Note:<br>
        supported hash type: MD5, BitLocker, 7-Zip, WinZip, RAR5<br>
        supported attack type: Straight, Combination, Brute-force, Hybrid Wordlist + Mask, Hybrid Mask + Wordlist, Association<br>
    Expected response :<br>
        urrl to file with plaintext of given hash if cracked 
    """
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

        command = create_hashcat_command_general(hashcat_input_dict)
        # Start the process with Popen for real-time output
        if hashcat_running_output: text = True
        else: text = False

        session_name = str(uuid.uuid4())
        command.append('--session')
        command.append(session_name)
        command.append('--backend-ignore-opencl')
        command[0] = hashcat_path
        cm = " ".join(command)
        print ('-------------------') 
        print (command)
        print('')
        print (cm)           
        with open(os.path.join(current_dir,'command.txt'), 'a') as f:
            f.write('\n\n\n')
            f.write(cm)
        RESTORE = True
        first_flag = True
        exhausted_flag = False
        crack_all_flag = False
        terminate_intent = False
        start = time.time()

        while RESTORE: # until no more restore due to heat 
                if first_flag == False:
                        print (f'cooling gpu for {COOLDOWN_TIME_GPU} seconds')
                        time.sleep(COOLDOWN_TIME_GPU) # 
                        print ('------------- REBORN SESSION --------------')
                        command = [hashcat_path, '--session', session_name, '--restore']
                else:
                        first_flag = False
                        RESTORE = False
                process = subprocess.Popen(command, 
                            cwd="hashcat", 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            stdin=subprocess.PIPE,
                            text=text, 
                            shell=False, # shell == False needs hashcat to be hashcat path, False for less error chance for cracking 
                            encoding='utf-8'
                            )
                time.sleep(terminal_crack_warmup_time) # for restart slow terminal 
                flag = False
                for line in process.stdout:
                    # in case it is still hot,  
                    # but hashcat done, no need to restore anymore 
                    if ": Exhausted" in line: 
                        exhausted_flag = True
                        RESTORE = False # escape hashcat , no more reborn 
                    elif ": Cracked" in line: 
                        RESTORE = False # escape hashcat , no more reborn
                        crack_all_flag = True
                    elif ": Aborted" in line: 
                        print ('gpu self Aborted, maybe by temp')
                        print ('last temp recorded: ', last_temp)
                        RESTORE = True # if die due to heat , reborn
                        ABORT_SIGNAL = False
                        kill_process(process)     
                        break  # Exit the loop after terminating
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
                    period = time.time() - start
                    if period > 5: # check every 5 seconds if receive terminate signal
                        start = time.time()
                        with open (hashcat_terminate_file, 'r', encoding='utf-8') as f:
                            if 'terminate' in f.read().lower():
                                print('TERMINATE SIGNAL RECEIVED')
                                kill_process(process)     
                                terminate_intent = True
                                RESTORE = False # escape hashcat , no more reborn 

        # terminate_hashcat(process)
        _, stderr = process.communicate()

        # Handle stderr if any
        if stderr:
            if "No hashes loaded" in stderr:
                message = "No hash found in file OR hashcat_hash_code is not correct with hash in file"
                reply_bad_request(message=message)
            else:
                reply_bad_request(message=stderr)
        kill_process(process)
        url_output = f"http://{host_ip}:{port_num}/static/cracked_hash/{output_file_name}"
        ### check for result 
        output_file_path = os.path.join(cracked_hash_result_folder, output_file_name)
        # if not os.path.exists(output_file_path):
        # if exhausted_flag:
        #     message = "Wordlist Exhausted. Cannot crack ALL hash. Maybe have crack some hashes. Try find more wordlists to crack the rest hashes"
        #     return reply_success(message = message,
        #                                 result = None)
        if not os.path.exists(output_file_path):
            return reply_server_error('server suddenly cancel the cracking process')
        with open (output_file_path, 'r') as f: 
            with open (hash_file, 'r') as hf:
                hf_data = hf.readlines()
                miss = 0 
                for item in hf_data:
                    if item.strip().strip('\n').strip('\t') == "":
                        miss += 1 
        path = fix_path(os.path.join(cracked_hash_result_folder, output_file_name))

        if terminate_intent:
            message = "TERMINATE SIGNAL RECEIVED. taking last checkpoint session. saving hash cracked so far"
            with open (backend_temp_output, 'r', encoding='utf-8') as f:
                data = f.readlines()
                progress_phase = data[0]
            return reply_success(message = message,
                                        result = {'progress_phase':progress_phase, 
                                                  'session_name':session_name,
                                                  'path': path,
                                                  'url': url_output})
        if crack_all_flag:
            message = "Sucessfully crack ALL hashes"
            return reply_success(message = message,
                                result = {"path": path,
                                            "url": url_output})
        if exhausted_flag:
            message = "Wordlist Exhausted. Sucessfully crack these hashes"
            return reply_success(message = message,
                                result = {"path": path,
                                            "url": url_output})

    except Exception as e:
        return reply_server_error(e)


# Define your condition checker
# def check_condition(line):
#     """
#     Replace this function's logic with your actual condition.
#     For example, terminate when a certain number of hashes are cracked.
#     """
#     # Example condition: terminate when "Cracked: 100" appears in output
#     if "Cracked: 100" in line:
#         return True
#     return False

# # Define the termination handler
# def terminate_hashcat(process):
#     """
#     Sends the 'q' command to Hashcat's stdin to terminate it.
#     """
    
#     try:
#         if process.poll() is None:  # Check if process is still running
#             print("Condition met. Sending 'q' to terminate Hashcat...")
#             process.stdin.write('q\n')  # Send 'q' followed by newline
#             process.stdin.flush()        # Ensure the command is sent immediately
#             return 
#     except Exception as e:
#         print(f"Error sending 'q': {e}")
    
# Define the output reader
# def read_output(process, on_condition_met):
#     """
#     Reads the subprocess's stdout line by line.
#     Calls on_condition_met() when the condition is satisfied.
#     """
#     tmp = []
#     flag = False
#     for line in process.stdout:
#         # Process the output as per your original logic
#         if "Session..........: " in line:
#             tmp = []
#             flag = True
#         if "Hardware.Mon." in line:
#             tmp.append(line)
#             flag = False
#             with open(hashcat_temp_output, 'w', encoding='utf-8', errors='ignore') as f:
#                 for tmp_line in tmp:
#                     f.write(tmp_line)
#         if flag:
#             tmp.append(line)
#         if hashcat_running_output:
#             print(line, end='')  # Print the output in real-time

#         # Check if the line meets the condition
#         if check_condition(line):
#             on_condition_met(process)
#             break  # Exit the loop after condition is met

#     # Continue reading remaining output if necessary
#     for line in process.stdout:
#         if hashcat_running_output:
#             print(line, end='')

# while RESTORE_HASHCAT:
    # Start the subprocess with stdin enabled
    # process = subprocess.Popen(
    #     command,
    #     cwd="hashcat",
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    #     stdin=subprocess.PIPE,  # Enable stdin to send commands
    #     text=text,              # Use text mode for easier string handling
    #     shell=True,            # Use shell=False for security
    #     encoding='utf-8'
    # )
    # output_thread = threading.Thread(target=read_output, args=(process, terminate_hashcat))
    # output_thread.start()
    # output_thread.join()

    # Wait for the process to terminate and get stderr

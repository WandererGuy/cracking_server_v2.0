from fastapi import Form, APIRouter
import os 
import configparser
import subprocess
from utils.common import empty_to_none, fix_path, generate_unique_filename, attack_mode_translate, \
                            data_type_translate, check_value_in_dict, attack_mode_dict, hash_type_dict
from routers.model import reply_bad_request, reply_success, reply_server_error
from utils.common import empty_to_false
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(detail)s', filename='fastapi.log', filemode='w')
# logger = logging.getLogger(__name__)

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
config_path = os.path.join(parent_dir,'config.ini')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
hashcat_running_output = config['DEFAULT']['hashcat_running_output'] 
hashcat_running_output = empty_to_false(hashcat_running_output)
# Construct the path to config.ini
static_path = os.path.join(parent_dir,'static')
crack_collection = os.path.join(static_path, "potfiles", "potfile.txt")
session_folder = os.path.join(parent_dir, "session")
cracked_hash_result_folder = os.path.join(static_path, 'cracked_hash')
potfile_folder = os.path.join(static_path, "potfiles")
hashcat_temp_output = os.path.join(static_path,'hashcat_temp_output.txt')


    
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
            "session_name": '--session',
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
    gpu_number: str = Form(None)
):
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
    session_name = generate_unique_filename(session_folder , extension="restore")
    output_file_name = generate_unique_filename(cracked_hash_result_folder , extension="txt")
    output_file = os.path.join(cracked_hash_result_folder, output_file_name)
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
        "session_name": session_name,
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
        cm = " ".join(command)
        print ('-------------------') 
        print (command)
        print('')
        print (cm)           
        # process = subprocess.run(command,
        #                         capture_output=True, 
        #                         cwd="hashcat",
        #                         shell=True,
        #                         text=True, 
        #                         encoding = 'utf-8')
        # # wrong ccommand will return nothing 
        # if process.stderr:
        #     if "No hashes loaded" in process.stderr:
        #         message = "No hash found in file OR hash_type is not same type with loaded hash"
        #         return reply_bad_request(message = message)
        #     return reply_bad_request(message = process.stderr)
        # Start the process with Popen for real-time output
        if hashcat_running_output: text = True
        else: text = False
        with subprocess.Popen(command, 
                            cwd="hashcat", 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            text=text, 
                            shell=True,
                            encoding='utf-8') as process:
                # Read and print output line by line as it comes

                flag = False
                for line in process.stdout:
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
            # Optionally, handle stderr (error output)
                _, stderr = process.communicate()
                if stderr:
                    if "No hashes loaded" in stderr:
                        message = "No hash found in file OR hashcat_hash_code is not correct with hash in file"
                        return reply_bad_request(message = message)
                    return reply_bad_request(message = stderr)




        url_output = f"http://{host_ip}:{port_num}/static/cracked_hash/{output_file_name}"
        ### check for result 
        output_file_path = os.path.join(cracked_hash_result_folder, output_file)
        if not os.path.exists(output_file_path):
            message = "Wordlist Exhausted. Cannot crack hash. Maybe find more wordlists"
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
            # if len(cracked_data_lines) < len(hf_data) - miss:
            #     message = f"cracked {len(cracked_data_lines)} over {len(hf_data)} hashes"
            #     return reply_success(message = message,
            #                         result = {"path": os.path.join(cracked_hash_result_folder, output_file_name),
            #                                 "url": url_output})
        message = "Sucessfully crack these hashes"
        return reply_success(message = message,
                            result = {"path": fix_path(os.path.join(cracked_hash_result_folder, output_file_name)),
                                      "url": url_output})

    except Exception as e:
        return reply_server_error(e)
    

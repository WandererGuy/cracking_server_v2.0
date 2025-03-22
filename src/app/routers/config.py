"""
in src\app\routers\backend\crack_only_hash.py
"""

flow_component = {
    'target_wl': 0,
    'target_wl_small_rule': 0,
    'small_trawling_wl': 1,
    'small_trawling_wl_small_rule': 1,
    'big_trawling_wl': 1,
    'big_trawling_wl_small_rule': 1,
    'small_target_ml': 0,
    'small_target_ml_small_rule': 0,
    'big_target_ml': 0,
    'big_target_ml_small_rule': 0,
    'small_trawling_ml': 1,
    'small_trawling_ml_small_rule': 1,
    'big_trawling_ml': 1,
    'big_trawling_ml_small_rule':   1,
    'first_desperate_ml': 1,
    'big_trawling_wl_big_rule': 1

}





hashcat_hash_code_dict = {
    "0": ["0"],
    "$zip2$": ["13600"],
    "$pkzip2$": ["17200", "17210", "17220", "17225", "17230"],
    "$rar5$": ["13000"],
    "$bitlocker$": ["22100"],
    "$7z$": ["11600"]
}

hash_type_to_hashcat_hash_code_dict = {
    "BitLocker": ["22100"],
    "7-Zip": ["11600"],
    "WinZip": ["13600", "17200", "17210", "17220", "17225", "17230"],
    "RAR5": ["13000"],
    "MD5": ["0"]
}





support_file_type = ['BitLocker', '7-Zip', 'WinZip', 'RAR5']


'''
no need to be in any order
'''
ls = [0, 22100, 11600, 13600, 13000, 17200, 17210, 17220, 17225, 17230]
hash_type_dict = {}
for item in ls:
    hash_type_dict[str(item)] = item

def gen_extract_command(hash_type, file_path):
    match hash_type:
        case "BitLocker":
            command = [
                'bitlocker2john',
                '-i',
                file_path
            ]
            
        case "7-Zip":
            command = [
                '7z2john',
                file_path
            ]        
        case "WinZip":
            command = [
                'zip2john',
                file_path
            ]
        case "RAR5":
            command = [
                'rar2john',
                file_path
            ]
        case _:
            return "Default case"
    return command

def find_hash(file_type, stdout):
    # real_hash = None
    print ('------------------ file_type ------------------')
    print (file_type)
    if file_type == "RAR5":
        border = ':'
        real_hash = stdout.split(border)[1]
        return real_hash
    elif file_type == "WinZip":
        check = "$zip2$"
        if check in stdout:
            real_hash = stdout.split(check, 1)[1]
            check_2 = "zip2$"
            real_hash = check + real_hash.split(check_2, 1)[0] + check_2
            return real_hash

        check = "$pkzip2$"
        if check in stdout:
            real_hash = stdout.split(check, 1)[1]
            check_2 = "pkzip2$"
            real_hash = check + real_hash.split(check_2, 1)[0] + check_2
            return real_hash
    elif file_type == "BitLocker":
        check = "User Password hash:"
        if check in stdout:
            real_hash = stdout.split(check, 1)[1]
            check_2 = "$bitlocker$"
            real_hash = stdout.split(check_2, 1)[1]
            check_3 = "Hash type: User Password with MAC verification"
            real_hash = check_2 + real_hash.split(check_3, 1)[0]
            real_hash = real_hash.strip('\n')
            return real_hash
    elif file_type == "7-Zip":
        border = ':'
        real_hash = stdout.split(border)[1]
        return real_hash
    else: return None


from utils.common import fix_path
from routers.model import reply_bad_request, reply_success
import os 
from tqdm import tqdm
def write_to_remaining_hashfile(remaining_hash_file, uncracked_hashes):
    with open (remaining_hash_file, 'w', encoding = 'utf-8') as f:
        for hash in uncracked_hashes:
            f.write(f'{hash}\n')

def end_cracking(cracked_hashes, new_cracked_hash_file, url_cracked_hash):
    with open (new_cracked_hash_file, 'w', encoding = 'utf-8') as f:
        for key, value in cracked_hashes.items():
            f.write(f'{key}:{value}\n\n\n')
    path = fix_path(new_cracked_hash_file)
    print ('written result in ', path)
    filename = os.path.basename(path)
    url = url_cracked_hash + filename
    return reply_success(message = 'Successfully cracked ALL hashes', 
                            result = {"path_cracked_hash": path, 
                                        "url_cracked_hash": url}) 
def end_cracking_by_terminate(cracked_hashes, cracked_hash_file, url_cracked_hash):
    
    print ('writing cracked hashes to file for display')
    with open (cracked_hash_file, 'w', encoding = 'utf-8') as f:
        for key, value in tqdm(cracked_hashes.items(), total = len(cracked_hashes)):
            f.write(f'{key}:{value}\n\n\n')
    path = fix_path(cracked_hash_file)
    print ('written result in ', path)
    filename = os.path.basename(path)
    url = url_cracked_hash + filename
    return reply_success(message = 'Terminate cracking, Successfully cracked these hashes so far', 
                            result = {"path_cracked_hash": path, 
                                        "url_cracked_hash": url}) 

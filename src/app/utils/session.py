import pandas as pd
import os
import uuid
import time
from utils.common import fix_path
def session_save(excel_path, 
                 session_folder_path, 
                 hash_file, 
                 res, 
                 original_extracted_file_path):
    df = pd.read_excel(excel_path)
    columns = df.columns
    for hash, hashcat_hash_code in res.items():
        name_single_hash_file = str(uuid.uuid4()) + '.txt'
        folder_1 = os.path.join(session_folder_path, hashcat_hash_code)
        os.makedirs(folder_1, exist_ok=True)
        file_1 = os.path.join(folder_1, name_single_hash_file)
        all_same_hashcat_hash_code_file = os.path.join(folder_1, 'all.txt')
        with open(file_1, 'w') as f:
            f.write(hash)
        with open(all_same_hashcat_hash_code_file, 'a') as f:
            f.write(hash)
            f.write('\n')
        final_row = {}
        if hash_file != None:
            new_row = {
                    'crack status': 'Non-cracked',
                    'time created': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'hash value in file': fix_path(file_1), 

                    'original hash file path': fix_path(hash_file), 

                    'hashcat hash code': hashcat_hash_code, 
                    'hashes same hashcat hash code in file': fix_path(all_same_hashcat_hash_code_file), 
                    'hash value': hash
                   }
        else:
            new_row = {
                    'crack status': 'Non-cracked',
                    'time created': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'hash value in file': fix_path(file_1), 

                    'original extracted file path': fix_path(original_extracted_file_path), 
                  
                    'hashcat hash code': hashcat_hash_code, 
                    'hashes same hashcat hash code in file': fix_path(all_same_hashcat_hash_code_file), 
                    'hash value': hash
                    }
        for col in columns:
            if col in new_row.keys():
                final_row[col] = new_row[col]
        df = pd.concat([df, pd.DataFrame([final_row])], ignore_index=True)
    df.to_excel(excel_path, index=False)

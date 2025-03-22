import uuid
import os 
import pandas as pd 
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
static_path = os.path.join(parent_dir,'static')
session_folder = os.path.join(static_path, 'session')
def create_session():
    session_id = str(uuid.uuid4())
    session_path = os.path.join(session_folder, session_id)
    os.makedirs(session_path, exist_ok=True)
    return session_path

def create_empty_df():
    columns = ['time created',
               'crack status',
               'plaintext password', 
               'hashcat hash code',
            'original extracted file path', 
            'original hash file path', 
            'hash value in file', 
            'hashes same hashcat hash code in file', 
            'hash value']
    df = pd.DataFrame(columns=columns)
    return df

def main():
    session_folder_path = create_session()
    df = create_empty_df()
    excel_file = os.path.join(session_folder_path, 'session.xlsx')
    df.to_excel(excel_file, index=False, engine='openpyxl')
    return os.path.basename(session_folder_path)

# class Hash:
#     def __init__(self, input_dict, df):
#         # Initialize attributes from the dictionary
#         self.hash_value_in_file = input_dict.get('hash value in file', "")
#         self.original_extracted_file_path = input_dict.get('original extracted file path', "")
#         self.original_hash_file_path = input_dict.get('original hash file path', "")
#         self.hashcat_hash_code = input_dict.get('hashcat hash code', "")
#         self.hash_same_hashcat_hash_code_in_file = input_dict.get('hash same hashcat hash code in file', "")
#         self.plaintext = input_dict.get('plaintext password', "")
#         self.df = df
#     # Method to display the information of the file
#     # Method to add the Hash object information to the DataFrame
#     def add_to_df(self):
#         # Create a new row as a dictionary
#         new_row = {
#             'hash value in file': self.hash_value_in_file,
#             'original extracted file path': self.original_extracted_file_path,
#             'original hash file path': self.original_hash_file_path,
#             'hashcat hash code': self.hashcat_hash_code,
#             'hash same hashcat hash code in file': self.hash_same_hashcat_hash_code_in_file,
#             'plaintext password': self.plaintext
#         }
#         # Append the new row to the DataFrame
#         self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
#         return self.df




# # Adding data to the empty DataFrame using .loc
# input_data = {
#         'hash value in file': "", 
#         'original extracted file path': "", 
#         'original hash file path': "", 
#         'hashcat hash code': "", 
#         'hash same hashcat hash code in file': "", 
#         'plaintext password': ""
#         }
# hash_info = Hash(input_data)



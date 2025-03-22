from utils import *
import sqlite3
from collections import Counter
import pandas as pd 

# top_common_passwords('tbl_30k')
# top_common_domain('tbl_30k')
# top_common_passwords_len('tbl_30k')
# top_common_substring_per_len('tbl_30k')
# show_password_given_substring(table_name, 'manh264')

zodiac_ls = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']
letter_list = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
digit_list = '0123456789'
symbol_list = '!@#$%^&*()-_=+[]{};’:”,./<>?'

table_name = 'tbl_30k'
domain_attack = 'gmail.com.vn'
min_len = 8

conn = sqlite3.connect('30k.db')
c = conn.cursor ()

def policy_filter(policy_code):
    pass


### get username and password with setting 
def preprocess(table_name):
    c.execute(f"""
        SELECT MIN(username) AS username, password, LENGTH(password) AS password_length
        FROM {table_name}
        WHERE LENGTH(password) >= {min_len} AND username LIKE '%@{domain_attack}'
        GROUP BY password
        ORDER BY LENGTH(password) ASC, username ASC
    """)

    data = c.fetchall()
    format_username = []
    format_password = []
    user_dict = {}
    chunk_user_dict = {}
    count = 0 
    txt_file_name = 'yahoo_30k.txt'
    for username, password, length in data:
        username = username.split('@')[0]
        password = password.strip().strip('\n')

        format_username.append(format(username))
        format_password.append(format(password))


        user_dict[str(count)] = {}
        user_dict[str(count)]['username'] = username
        user_dict[str(count)]['password'] = password
        # Write username and password to the file, each on a new line
        # file = open(txt_file_name, "w")
        # file.write(f"username: {username}\tpassword: {password}\n")

        for i in range (len(user_dict)):
            username = user_dict[str(i)]['username']
            password = user_dict[str(i)]['password']


            chunk_user_dict[str(i)] = {}

            # print('*******USERNAME*******')
            sequence = transform_string(username)
            chunk_string_list = chunk_string(username, sequence) 
            chunk_user_dict[str(i)]['username'] = chunk_string_list
            # print('*******PASSWORD*******')
            sequence = transform_string(password)
            chunk_string_list = chunk_string(password, sequence) 
            chunk_user_dict[str(i)]['password'] = chunk_string_list
        count += 1 
    print (chunk_user_dict)

    return format_username, format_password


# format_username, format_password = preprocess(table_name)

# top_10_common(format_username, save_type = 'USERNAME')
# print ('****************')
# top_10_common(format_password, save_type = 'PASSWORD')

def txt_to_excel():
    # Read the uploaded file
    file_path = 'yahoo_30k.txt'

    # Initialize lists to hold the usernames and passwords
    usernames = []
    passwords = []

    # Open and read the file
    with open(file_path, 'r') as file:
        for line in file:
            # Split each line by the tab character, assuming that's the separator
            parts = line.strip().split('\t')
            if len(parts) == 2:  # Make sure the line is properly formatted
                username, password = parts
                usernames.append(username.replace('username: ', '').strip())
                passwords.append(password.replace('password: ', '').strip())

    # Create a DataFrame from the lists
    df = pd.DataFrame({'Username': usernames, 'Password': passwords})

    # Save the DataFrame to an Excel file
    excel_path = 'yahoo_30k.xlsx'
    df.to_excel(excel_path, index=False)

# txt_to_excel()


# str = 'nam.awesome'

# # ver1 = extract_meaningful_chunks_NAME_WORD_CHAR(str)
# ver2 = extract_meaningful_chunks_WORD_NAME_CHAR(str)
# print ('***********************')
# # print (ver1)
# print (ver2)

# common_elements, different_elements_list1, different_elements_list2 = find_common_and_different_elements(ver1, ver2)
# print (common_elements)
# print (different_elements_list1)
# print (different_elements_list2)

# file_path = 'yahoo_30k.xlsx'
# output_path = 'yahoo_30k_transformed.xlsx'
# process_and_save_excel_data(file_path, output_path)

# Function definitions for generating combinations based on the provided constraints


# Python3 program to 
# generate all passwords
# for given characters
 
# Recursive helper function, 
# adds/removes characters
# until len is reached
from datetime import datetime

startTime = datetime.now()
import itertools
import time 
password = ''
digit_lst = ['1','2','3','4','5','6','7','8','9']
objects = ['duong', 'duc', 'manh']

max_item = 8 
objects = digit_lst + objects + digit_lst
def get_combinations(lst): # creating a user-defined method
   combination = [] # empty list 
   # max len(lst) + 1
   for r in range(1, max_item + 1):
      print ('Done all combinations with', r, 'items')
      # to generate combination
      combination.extend(itertools.combinations(lst, r))
   return combination

all_combinations = get_combinations(objects) # method call

all_predict = []
for combination in all_combinations:
    predict = ''
    for item in combination:
        predict = predict + item
    all_predict.append(predict)

with open('all_predict.txt', 'w') as f:
    for item in all_predict:
        f.write(item)
        f.write('\n')
print (f'with {len(objects)} keywords in user dict')
print (f"We generated all {len(all_predict)} possible passwords in", datetime.now() - startTime)
print ("Our password is", all_predict.index(password), "in the list of all passwords")
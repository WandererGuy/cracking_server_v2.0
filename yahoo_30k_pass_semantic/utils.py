import sqlite3
from collections import Counter
import matplotlib.pyplot as plt


conn = sqlite3.connect('30k.db')
c = conn.cursor ()




def init_table(new_table_name):
    c.execute(f"""CREATE TABLE IF NOT EXISTS {new_table_name} (
            username TEXT,
            password TEXT
            )
            """)
    conn.commit()
    conn.close()
    print ("Done init_table")

def insert_data_into_table(txt_name, table_name):
    with open(txt_name, 'r') as file:
        # Read each line from the file
        for line in file:
            # Split each line into username and password
            if '@' in line :

                username, password = line.strip().split(':')
                # Insert username and password into the database
                c.execute(f"INSERT INTO {table_name} (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    print("Done insert_data_into_table")



def plot_top_10_elements(data, save_type):
        # Let's make the plotting dynamic, allowing for any length of input data.
    elements, occurrences, percentages = zip(*data)
    # Assuming 'elements', 'occurrences', and 'percentages' lists are provided, and could be of any length.
    # For demonstration, I'll use the same lists but the code will automatically adjust to the list lengths.

    # Trimming the lists to the top 10 for this example (but the code will work for any length).
    top_n = 10
    elements_top = elements[:top_n]
    occurrences_top = occurrences[:top_n]
    percentages_top = percentages[:top_n]

    # Plotting dynamically
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Twin axis for percentages
    ax2 = ax1.twinx()
    ax1.bar(elements_top, occurrences_top, color='g')
    ax2.plot(elements_top, percentages_top, color='b', marker='o', linestyle='-', linewidth=2)

    # Setting the axes labels
    ax1.set_xlabel('Elements')
    ax1.set_ylabel('Occurrences', color='g')
    ax2.set_ylabel('Percentage (%)', color='b')

    # Setting the x-axis labels dynamically
    ax1.set_xticks(range(len(elements_top)))
    ax1.set_xticklabels(elements_top, rotation=45, ha="right")

    plt.title(f'Top 10 Most Common Elements in {save_type}: Occurrences and Percentages')
    plt.tight_layout()  # Adjusts subplot params to give some padding.
    plt.savefig(f'top_10_common_{save_type}.png')

def top_10_common(given_list, save_type):
        element_counts = Counter(given_list)
        # Use most_common(10) to get the top 10 most common elements
        top_10_common_elements = element_counts.most_common(20)
        print("Top 10 most common elements:")

        element_list = []
        count_list = []
        percentage_list = []
        for element, count in top_10_common_elements:
            element_list.append(element)
            count_list.append(count)
            percentage_list.append(round(count/len(given_list)*100, 2))
            data = list(zip(element_list, count_list, percentage_list))
        # Print the top 10 most common elements
        for element, count in top_10_common_elements:
            print(f"{element}: {count} occurrences, percentage: {count/len(given_list)*100:.2f}%")
        
        plot_top_10_elements(data, save_type)

def top_common_passwords(table_name):
    c.execute(f"""
        SELECT password, COUNT(*) AS count
        FROM {table_name}
        GROUP BY password
        ORDER BY count DESC
        LIMIT 10
    """)

    # Fetch the results
    top_passwords = c.fetchall()

    # Print the top 10 most common passwords
    print("**************** Top 10 most common passwords: ****************")
    for password, count in top_passwords:
        print(f"Password: {password}, Count: {count}")

def top_common_domain(table_name):
        c.execute(f"""
                SELECT username
                FROM {table_name}
                WHERE username LIKE '%@%'
                GROUP BY username
                """
                )
        # Fetch the results
        items = c.fetchall()
        domain_list = []
        for item in items:
            # if 'sis.hust.edu.vn' in item[0] and '19' in item[0]:
            #     print (item[0])
            domain_name = (item[0].split('@')[1])
            domain_list.append(domain_name)
        print("**************** Top 10 most common domain name: ****************")

        # Use Counter to count occurrences of each element
        top_10_common(domain_list, 'DOMAIN')
        print ('Done')
        

# most common password length 
def top_common_passwords_len(table_name):
    length_ls = []
    c.execute(f"""
        SELECT password, LENGTH(password) AS password_length
        FROM {table_name}
        GROUP BY password
    """)

    # Fetch the results
    top_passwords = c.fetchall()

    # Print the top 10 most common passwords
    print("**************** Top 10 most common distinct passwords length: ****************")
    for password, length in top_passwords:
        length_ls.append(length)
    # Use Counter to count occurrences of each element
    element_counts = Counter(length_ls)

    # Use most_common(10) to get the top 10 most common elements
    top_10_common_len = element_counts.most_common(10)

    # Print the top 10 most common elements
    for element, count in top_10_common_len:
        print(f"length {element}: {count} occurrences")
    print ('Done')



def top_common_substring_per_len(table_name):
    c.execute(f"""
        SELECT password
        FROM {table_name}
        GROUP BY password
    """)

    # Fetch the results
    passwords = c.fetchall()
    all_substr = []
    for test_str in passwords:
        test_str = test_str[0]
        # Get all substrings of string
        # Using list comprehension + string slicing
        res = [test_str[i: j] for i in range(len(test_str))
                for j in range(i + 1, len(test_str) + 1)]
        for item in res:
            all_substr.append(item)

    temp_ls = []
    for i in range (2,12,1):
        for item in all_substr:
            if len(item) == i:
                temp_ls.append(item)
        print ('****************Most common substring with length ', i, '****************')
        top_10_common(temp_ls, 'COMMON_SUBSTRING')
        temp_ls = []


def show_password_given_substring(table_name, substring):
    password_ls =[]
    c.execute(f"""
        SELECT password
        FROM {table_name}
        GROUP BY password
    """)
    # Fetch the results
    passwords = c.fetchall()
    for item in passwords:
        if substring in item[0]:
            password_ls.append(item[0])
    print ('****************Password with substring ', substring, '****************')
    for item in password_ls:
        print (item)
    print ('there are ',len(password_ls), ' elements in this list' )


def substring_common_2_columns(table_name):
    c.execute(f"""
        SELECT username, password
        FROM {table_name}
              """
              )
    data = c.fetchall()
    
    for username, password in data:
        username = username.lower()
        password = password.lower()
        username_substring = []
        password_substring = []
        common_substring = []
        res = [username[i: j] for i in range(len(username))
        for j in range(i + 1, len(username) + 1)]
        for item in res:
            username_substring.append(item)

        res = [password[i: j] for i in range(len(password))
        for j in range(i + 1, len(password) + 1)]
        for item in res:
            password_substring.append(item)    
        for item in username_substring:
            if len(item) > 1:
                if item in password_substring:
                    common_substring.append(item)
        if common_substring == []:
            max_len_string = 'None'
        else: 
            max_len_string = max(common_substring, key=len)
        print (f"username: {username}, password: {password}, common_substring: {max_len_string}")
                       



### format string into format like L4D3S1L3 : letter 4 digit 3 symbol 1 letter 3
def transform_string(str): 
    sequence = ""
    for i in range(len(str)): 
        if (str[i].isdigit()): 
            sequence += 'D'
        elif((str[i] >= 'A' and str[i] <= 'Z') or
                (str[i] >= 'a' and str[i] <= 'z')): 
            sequence += 'L'
        else:
            sequence += 'S'
    return sequence

def chunk_string(s, sequence):
    chunk_list = []
    temp_sequence = ""
    for index, i in enumerate(range(len(s))): 
        if index >= 1:
            if sequence[i] == sequence[i-1] and index == len(s)-1:
                temp_sequence += s[i]
                chunk_list.append(temp_sequence)
            elif sequence[i] == sequence[i-1]:
                temp_sequence += s[i]
            elif sequence[i] != sequence[i-1] and index == len(s)-1:
                chunk_list.append(s[i])
            else:
                chunk_list.append(temp_sequence)
                temp_sequence = ''
                temp_sequence += s[i]
        else: 
            temp_sequence += s[i]
    return chunk_list

def transform_string_with_counts(s):
    result = ""
    i = 0
    while i < len(s):
        count = 1
        while i + 1 < len(s) and s[i] == s[i + 1]:
            count += 1
            i += 1
        result += s[i] + str(count)
        i += 1
    return result

def format(string):
    sequence = transform_string(string)
    result = transform_string_with_counts(sequence)
    return result




import unicodedata

BANG_XOA_DAU = str.maketrans(
    "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
    "A"*17 + "D" + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "a"*17 + "d" + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5
)

def xoa_dau(txt: str) -> str:
        if not unicodedata.is_normalized("NFC", txt):
            txt = unicodedata.normalize("NFC", txt)
        return txt.translate(BANG_XOA_DAU)
    

def dict_transform():
    new_dict = []
    filename = 'Vietnamese_vi_VN.txt'
    file = open(filename, encoding="utf8")
    for index, line in enumerate(file):
        if index != 0 :
            new_line = xoa_dau(line.strip())
            if new_line in new_dict:
                continue
            else:
                new_dict.append(new_line)
                new_dict.append('\n')

    with open ('Vietnamese_vi_VN_transform.txt', 'w') as file_transform:
                file_transform.writelines(new_dict)

def name_transform():
    new_dict = []
    filename = 'boy.txt'
    file = open(filename, encoding="utf8")
    for index, line in enumerate(file):
            data = line.strip().replace('\n', '').lower().split(' ')
            if len(data) == 2:
                surname_, name_ = data
                surname = xoa_dau(surname_)
                name = xoa_dau(name_)
                if surname in new_dict:
                    pass
                else:
                    new_dict.append(surname)
                    new_dict.append('\n')
                if name in new_dict:
                    pass
                else:
                    new_dict.append(name)
                    new_dict.append('\n')

    with open ('boy_name_transform.txt', 'w', encoding="utf-8") as file_transform:
                file_transform.writelines(new_dict)


def merge_2_file():
    # Open the first file in read mode
    with open('girl_name_transform.txt', 'r') as file1:
        data_file1 = file1.read()

    # Open the second file in read mode
    with open('boy_name_transform.txt', 'r') as file2:
        data_file2 = file2.read()

    # Open a new file in write mode
    with open('name_dict.txt', 'w') as merged_file:
        # Write the contents of the first file
        merged_file.write(data_file1)
        # Optionally add a newline in between if you prefer
        merged_file.write("\n")
        # Write the contents of the second file
        merged_file.write(data_file2)

    print("Files merged successfully into 'merged_file.txt'")



def sort_substrings(substring_list, target_string):
    sorted_substrings = []
    index = 0
    while index < len(target_string):
        for substring in substring_list:
            # Check if the current index in the target string matches the substring
            if target_string.startswith(substring, index):
                sorted_substrings.append(substring)
                index += len(substring)  # Move past this substring in the target string
                break
        else:
            index += 1  # No substring match at current index, move to next character

    return sorted_substrings

letter_list = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
special_case = ['nguyen', 'quyen', 'chim','kiet','thanh']
### extract priority possible name first then all possible word then all possible charcter left 
def extract_meaningful_chunks_NAME_WORD_CHAR(str):
    name_list = open('name_dict.txt', encoding="utf8").readlines()
    word_list = open('Vietnamese_transform_dict.txt', encoding="utf8")
    # create chunk (based LDS)
    english_list = open('english_popular.txt', encoding="utf8")
    # create chunk (based LDS)
    sequence = transform_string(str)
    chunk_list = chunk_string(str, sequence)

    new_word_list = []
    for item in word_list:
        new_word_list.append(item.replace('\n', ''))
    new_name_list = []
    for item in name_list:
        new_name_list.append(item.replace('\n', ''))
    new_english_list = []
    for item in english_list:
        new_english_list.append(item.strip().replace('\n', ''))
    all_meaningful_chunk_list = []
    total_list = []

    
    # break down chunk (based priority max length substring match name, dict, rest word)
    for item in chunk_list:
        item = item.lower()
        flag_text = False
        for i in range(len(letter_list)):
            if letter_list[i] in item:
                flag_text = True
                meaning_chunk_list = []
                ori_item = item
                flag = True
                english_flag = False
                while True:

                    ### find all possible name from substring
                    res = [ori_item[i: j] for i in range(len(ori_item))
                    for j in range(i + 1, len(ori_item) + 1)]
                    substring_descend = sorted(res, key=len, reverse=True)
                    first_substring = substring_descend[0] #longest substring
                    if first_substring in new_english_list and len(first_substring) > 4:
                        
                        repeat = ori_item.count(first_substring)
                        ori_item = ori_item.replace(first_substring, ';')
                        for i in range(repeat):
                            meaning_chunk_list.append(first_substring)
                        print ('Found first english ', first_substring)
                    elif first_substring not in new_english_list and english_flag == False:
                        for i in range(len(substring_descend)):
                            if i > 0:
                                substring = substring_descend[i]
                                if substring in new_english_list and len(substring) > 4:
                                    repeat = ori_item.count(substring)
                                    ori_item = ori_item.replace(substring, ';')
                                    for i in range(repeat):
                                        meaning_chunk_list.append(substring)
                                    print ('Found english ', substring) 
                        english_flag = True

                    # if all substring > 4  dont have english word, still 
                    # return english flag = True to continue while loop for < 4 english word first substring
                    elif first_substring in new_english_list and english_flag == False and len(first_substring) <= 4:
                        english_flag = True
                    elif first_substring in new_name_list and english_flag:
                        repeat = ori_item.count(first_substring)
                        ori_item = ori_item.replace(first_substring, ';')
                        for i in range(repeat):
                            meaning_chunk_list.append(first_substring)
                    elif len(ori_item) > 0 and english_flag: 
                        found = False
                        for i in range(len(substring_descend)):
                            if i > 0:
                                substring = substring_descend[i]
                                if substring in new_name_list:
                                    repeat = ori_item.count(substring)
                                    ori_item = ori_item.replace(substring, ';')
                                    for i in range(repeat):
                                        meaning_chunk_list.append(substring)
                                    found = True
                                    break 
                        ### no name can be found from remaining substring, switch to find words
                        if first_substring in new_word_list and found == False:
                            repeat = ori_item.count(first_substring)
                            ori_item = ori_item.replace(first_substring, ';')
                            for i in range(repeat):
                                meaning_chunk_list.append(first_substring)
                            found = True
                        if first_substring not in new_word_list and found == False:
                            for i in range(len(substring_descend)):
                                if i > 0:
                                    substring = substring_descend[i]

                                    if substring in new_name_list:
                                        repeat = ori_item.count(substring)
                                        ori_item = ori_item.replace(substring, ';')
                                        for i in range(repeat):
                                            meaning_chunk_list.append(substring)
                                        found = True
                                        break 
                            if found == False:
                                ### find in word list 
                                for i in range(len(substring_descend)):
                                    if i > 0:
                                        substring = substring_descend[i]

                                        if substring in new_word_list:
                                            repeat = ori_item.count(substring)
                                            ori_item = ori_item.replace(substring, ';')
                                            for i in range(repeat):
                                                meaning_chunk_list.append(substring)
                                            found = True
                                            break 
                        if found == False :
                            flag = False
                            if ';' not in first_substring:
                                repeat = ori_item.count(first_substring)
                                ori_item = ori_item.replace(first_substring, ';')
                                for i in range(repeat):
                                    meaning_chunk_list.append(first_substring)

                            else:
                                for i in range(len(substring_descend)):
                                    if i > 0:
                                        substring = substring_descend[i]
                                        if ';' not in substring:

                                            repeat = ori_item.count(substring)
                                            ori_item = ori_item.replace(substring, ';')
                                            for i in range(repeat):
                                                meaning_chunk_list.append(substring)
                                            flag = True ### found substring not ;
                                            break 
                            if flag == False: ### only ; left                
                                print ('no more can be found from substring')
                                break
                sorted_meaning_chunk_list = meaning_chunk_list
                all_meaningful_chunk_list.append(sorted_meaning_chunk_list)
        # for item in all_meaningful_chunk_list:
        #     all_meaningful_chunk_list = [ [i for i in item if i != ';'] for item in all_meaningful_chunk_list]
                total_list.append(all_meaningful_chunk_list)
                break
        if flag_text == False:
            total_list.append(item)
# Sorting the list
    return total_list







### priority word before name 
def extract_meaningful_chunks_WORD_NAME_CHAR(str):
    word_list = open('name_dict.txt', encoding="utf8").readlines()
    name_list = open('Vietnamese_transform_dict.txt', encoding="utf8")
    # create chunk (based LDS)
    english_list = open('english_popular.txt', encoding="utf8")
    # create chunk (based LDS)
    sequence = transform_string(str)
    chunk_list = chunk_string(str, sequence)

    new_word_list = []
    for item in word_list:
        new_word_list.append(item.replace('\n', ''))
    new_name_list = []
    for item in name_list:
        new_name_list.append(item.replace('\n', ''))
    new_english_list = []
    for item in english_list:
        new_english_list.append(item.strip().replace('\n', ''))
    all_meaningful_chunk_list = []
    total_list = []

    
    # break down chunk (based priority max length substring match name, dict, rest word)
    for item in chunk_list:
        item = item.lower()
        flag_text = False
        for i in range(len(letter_list)):
            if letter_list[i] in item:
                flag_text = True
                meaning_chunk_list = []
                ori_item = item
                flag = True
                english_flag = False
                while True:

                    ### find all possible name from substring
                    res = [ori_item[i: j] for i in range(len(ori_item))
                    for j in range(i + 1, len(ori_item) + 1)]
                    substring_descend = sorted(res, key=len, reverse=True)
                    first_substring = substring_descend[0] #longest substring
                    if first_substring in new_english_list and len(first_substring) > 4:
                        
                        repeat = ori_item.count(first_substring)
                        ori_item = ori_item.replace(first_substring, ';')
                        for i in range(repeat):
                            meaning_chunk_list.append(first_substring)
                        print ('Found first english ', first_substring)
                    elif first_substring not in new_english_list and english_flag == False:
                        for i in range(len(substring_descend)):
                            if i > 0:
                                substring = substring_descend[i]
                                if substring in new_english_list and len(substring) > 4:
                                    repeat = ori_item.count(substring)
                                    ori_item = ori_item.replace(substring, ';')
                                    for i in range(repeat):
                                        meaning_chunk_list.append(substring)
                                    print ('Found english ', substring) 
                        english_flag = True

                    # if all substring > 4  dont have english word, still 
                    # return english flag = True to continue while loop for < 4 english word first substring
                    elif first_substring in new_english_list and english_flag == False and len(first_substring) <= 4:
                        english_flag = True
                    elif first_substring in new_name_list and english_flag:
                        repeat = ori_item.count(first_substring)
                        ori_item = ori_item.replace(first_substring, ';')
                        for i in range(repeat):
                            meaning_chunk_list.append(first_substring)
                    elif len(ori_item) > 0 and english_flag: 
                        found = False
                        for i in range(len(substring_descend)):
                            if i > 0:
                                substring = substring_descend[i]
                                if substring in new_name_list:
                                    repeat = ori_item.count(substring)
                                    ori_item = ori_item.replace(substring, ';')
                                    for i in range(repeat):
                                        meaning_chunk_list.append(substring)
                                    found = True
                                    break 
                        ### no name can be found from remaining substring, switch to find words
                        if first_substring in new_word_list and found == False:
                            repeat = ori_item.count(first_substring)
                            ori_item = ori_item.replace(first_substring, ';')
                            for i in range(repeat):
                                meaning_chunk_list.append(first_substring)
                            found = True
                        if first_substring not in new_word_list and found == False:
                            for i in range(len(substring_descend)):
                                if i > 0:
                                    substring = substring_descend[i]

                                    if substring in new_name_list:
                                        repeat = ori_item.count(substring)
                                        ori_item = ori_item.replace(substring, ';')
                                        for i in range(repeat):
                                            meaning_chunk_list.append(substring)
                                        found = True
                                        break 
                            if found == False:
                                ### find in word list 
                                for i in range(len(substring_descend)):
                                    if i > 0:
                                        substring = substring_descend[i]

                                        if substring in new_word_list:
                                            repeat = ori_item.count(substring)
                                            ori_item = ori_item.replace(substring, ';')
                                            for i in range(repeat):
                                                meaning_chunk_list.append(substring)
                                            found = True
                                            break 
                        if found == False :
                            flag = False
                            if ';' not in first_substring:
                                repeat = ori_item.count(first_substring)
                                ori_item = ori_item.replace(first_substring, ';')
                                for i in range(repeat):
                                    meaning_chunk_list.append(first_substring)

                            else:
                                for i in range(len(substring_descend)):
                                    if i > 0:
                                        substring = substring_descend[i]
                                        if ';' not in substring:

                                            repeat = ori_item.count(substring)
                                            ori_item = ori_item.replace(substring, ';')
                                            for i in range(repeat):
                                                meaning_chunk_list.append(substring)
                                            flag = True ### found substring not ;
                                            break 
                            if flag == False: ### only ; left                
                                print ('no more can be found from substring')
                                break
                sorted_meaning_chunk_list = meaning_chunk_list
                all_meaningful_chunk_list.append(sorted_meaning_chunk_list)
        # for item in all_meaningful_chunk_list:
        #     all_meaningful_chunk_list = [ [i for i in item if i != ';'] for item in all_meaningful_chunk_list]
                total_list.append(all_meaningful_chunk_list)
                break
        if flag_text == False:
            total_list.append(item)
# Sorting the list
    return total_list




def find_common_and_different_elements(list1, list2):
    # Find common elements
    common_elements = [element for element in list1 if element in list2]

    # Find elements in list1 not in list2 and vice versa
    different_elements_list1 = [element for element in list1 if element not in list2]
    different_elements_list2 = [element for element in list2 if element not in list1]

    return common_elements, different_elements_list1, different_elements_list2


import pandas as pd

# Function to load data from an Excel file

def load_data(file_path):
    return pd.read_excel(file_path)

def flatten_nested_list(nested_list, depth=0, results=None):
    if results is None:
        results = []
    if isinstance(nested_list, list):
        for item in nested_list:
            flatten_nested_list(item, depth + 1, results)  # recurse into sublist
    else:
        # Ensure there are enough columns
        while len(results) <= depth:
            results.append([])
        results[depth].append(nested_list)
    written_into_excel = ''
    for item in results:
        if item == []:
            pass
        else:
            for text in item:
                written_into_excel = written_into_excel + '"' + str(text) + '": ' + '\n'
    written_into_excel = written_into_excel.rstrip('\n')
    return written_into_excel


def personal_dict(input_string):
    # Split the string by lines
    lines = input_string.strip().split('\n')

    # Extract keys by splitting each line at the colon and stripping the quotation marks
    keys = [line.split(':')[0].strip().replace('"', '') for line in lines if line.strip()]
    return keys

import time 
def process_and_save_excel_data(file_path, output_file_path):
    # Load the data
    data = load_data(file_path)
    if 'Transformed Email' not in data.columns:
        data['Transformed Email'] = None
    if 'Transformed Password' not in data.columns:
        data['Transformed Password'] = None
    if 'Personal dictionary' not in data.columns:
        data['Personal dictionary'] = None
    data1 = data['Email prefix'].apply(extract_meaningful_chunks_WORD_NAME_CHAR).apply(flatten_nested_list)
    data2 = data['Password'].apply(extract_meaningful_chunks_WORD_NAME_CHAR).apply(flatten_nested_list)
    data['Transformed Email'] = data1
    data['Transformed Password'] = data2
    data['Personal dictionary'] = data['Transformed Email'].apply(personal_dict) + data['Transformed Password'].apply(personal_dict)
    # Insert transformed data into the two rightmost PII columns
    # Check if the columns exist, if not, create them
    # Assign the transformed values
    # Save the modified DataFrame to a new Excel file
    data.to_excel(output_file_path, index=False)
    print ("Data processed and saved to Excel successfully.")

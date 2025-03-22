
import os 
parent = r"C:\Users\Admin\CODE\work\PASSWORD_CRACK\PASSCRACK_MATERIAL\WORDLISTS\ALL_WORDLIST\all_wordlist_split\phone_vn_split"
for filename in os.listdir(parent):
     path = os.path.join(parent, filename)
     print (filename)
     os.rename(path, path + ".txt")

# # path = r"C:\Users\Admin\CODE\work\PASSWORD_CRACK\PASSCRACK_MATERIAL\WORDLISTS\ALL_WORDLIST\all_wordlist_split\other+002+seclist\unique_small.txt"
# path = r"C:\Users\Admin\CODE\work\PASSWORD_CRACK\PASSCRACK_MATERIAL\WORDLISTS\ALL_WORDLIST\all_wordlist_split\other+002+seclist\rockyousplit\rockyou2021_002.txt___aa"
# new_path = r"C:\Users\Admin\CODE\work\PASSWORD_CRACK\PASSCRACK_MATERIAL\WORDLISTS\ALL_WORDLIST\all_wordlist_split\other+002+seclist\rockyousplit\rockyou2021_002.txt___aa"
# from tqdm import tqdm
# # import chardet

# # Open the file in binary mode (read bytes)
# # with open(path, 'rb') as f:
# #     raw_data = f.read()
# #     result = chardet.detect(raw_data)
# #     print(f"Detected encoding: {result['encoding']}")
# #     print(f"Confidence: {result['confidence']}")

# # remove invalid line, non utf 8 and have space , unique in every 10**7
# # queue = []
# f0 = open(new_path, 'a', encoding='utf-8')
# queue = []
# queue_num = 10**7
# with open (path, 'r', encoding='utf-8', errors='ignore') as f:
#     lines = f.readlines()
# for index, line in tqdm(enumerate(lines), total=len(lines)):
#         if index % queue_num == 0:  
#             queue = set(queue)
#             print ('adding to file')
#             for item in tqdm(queue, total=len(queue)):
#                 f0.write(item)
#             f0.close()
#             queue = []
#             f0 = open(new_path, 'a', encoding='utf-8')
#         line = line.strip('\n')
#         if ' ' in line or '\t' in line:
#             continue 
#         else:
#             queue.append(line + '\n')
        

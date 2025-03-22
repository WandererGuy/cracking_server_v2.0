import os 
import itertools
from tqdm import tqdm
# start = ['01', '02', '03', '04', '05', '06', '07', '08', '09', 
#             '841', '842', '843', '844', '845', '846', '847', '848', '849',
#             '+841', '+842', '+843', '+844', '+845', '+846', '+847', '+848', '+849']
start = ['03', '04']


def add_prefix(wordlist, selection):
    print ('adding prefix')
    res = []
    for word in tqdm(wordlist, total=len(wordlist)):
        for i in selection:
            res.append(i + word)
    return res

def all_combo(nested_lst):
    
    tmp = []
    print ('mixing all digit list')
    combinations = list(itertools.product(*nested_lst))
    for item in tqdm(combinations, total=len(combinations)):
        i = str(''.join(map(str, item)))
        tmp.append(i)
    return tmp
            
import time 
digit = []
for i in range (0,10):
    digit.append(i)
tmp_nested_ls = []

f = open('phone_vn.txt', 'w')
f.close()
counting = 0 
rest_len = [8] # phone number have 2 start digit + 8 digits
for a,b in zip(start[::2], start[1::2]):
    selection = [a,b]
    print (selection)
    counting += 1 
    for count in rest_len:
        f = open(f'phone_vn/{str(counting)}.txt', 'a')

        for item in range (0, count):
            tmp_nested_ls.append(digit)
        wordlist = all_combo(tmp_nested_ls)
        res = add_prefix(wordlist, selection)
        del wordlist
        tmp_nested_ls = []
        print (len(res))
        for item in tqdm(res, total = len(res)):
            f.write(f'{item}\n')
        del res
        f.close()


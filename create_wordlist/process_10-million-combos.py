import os 

def extract_content(text):
    '''
    extract content from text with ' '  or '\t'
    return list of strings
    '''
    ls = text.split(' ')
    res = []
    for item in ls:
        res.extend(item.split('\t'))
    new_res = [item for item in res if item != '']
    return new_res 


f = 'refined_wordlists'
save_path = os.path.join(f,'10-million-combos.txt')
path = r'10-million-combos\10-million-combos.txt'


# encoding = detect_encoding(path)
# print (encoding)
# ISO-8859-1

import time 
start = time.time()
tmp = []
with open(path,'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
    for line in lines:
        try:
            line = line.strip('\n')
            ls = extract_content(line)
            tmp.extend(ls)
        except:
            continue

tmp = set(tmp)

with open(save_path,'w', encoding='utf-8') as f:
    for item in tmp:
        f.write(item + '\n')
        

end = time.time()
print (end - start)

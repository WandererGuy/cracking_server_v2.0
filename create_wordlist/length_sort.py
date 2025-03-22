import os
from tqdm import tqdm 
directory = os.path.dirname(os.path.abspath(__file__))
'''
script for handle all splitted wordlist then put password into file , password have same length
'''

MIN = 8
MAX = 20
tmp = {}
buffer_limit = 1000 # every 1000 then release 
# for i in range(MIN, MAX+1):
#     file = os.path.join(directory,str(i) + '.txt')
#     with open(file, "w") as f:
#         pass
def write_to_file(content_dict):
    for i in range(MIN, MAX+1):
        file = os.path.join(directory,str(i) + '.txt')
        with open(file, "a", encoding="utf-8") as f:
            for item in content_dict[str(i)]:
                f.write(item)

if __name__ == '__main__':
    for i in range(MIN, MAX+1):
        tmp[str(i)] = []

    for filename in tqdm(os.listdir(directory), total = len(os.listdir(directory))):
        if filename.endswith(".txt") and filename.startswith("x"):
            tmp_2 = tmp 
            count = 0 
            f = os.path.join(directory, filename)
            with open(f, "r", encoding="utf-8") as file:
                lines = file.readlines()
                len_lines = len(lines)
                for i, line in tqdm(enumerate(lines), total = len(lines)):
                    line = line.strip('\n')
                    if i == len_lines - 1:
                        write_to_file(content_dict = tmp_2)
                    if count == buffer_limit:
                        write_to_file(content_dict = tmp_2)
                        tmp_2 = tmp
                        count = 0
                    if len(line) < MIN or len(line) > MAX:
                        continue
                    tmp_2[str(len(line))].append(line + '\n')
                    count += 1


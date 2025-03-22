def calculate_keyspace(mask):
    d = {'?d':10, '?l':26,'?a':94, '?s':32, '?u':26, '?h':16, '?H': 16}
    keyspace = 0
    for key, value in d.items():
        occurrences = mask.count(key)
        keyspace += value ** occurrences
    return keyspace



def split_file_into_small_big(path, limit_small_keyspace, limit_big_keyspace):
    t = "" 
    for item in path.split(".")[:-1]:
        t += item + '.'
    t = t[:-1]
    small_path = t + "_small" + '.hcmask'
    big_path = t + "_big" + '.hcmask'
    small_ls = []
    big_ls = []
    small_keyspace_total = 0
    big_keyspace_total = 0
    possible_keyspace = 0
    index = 0 # for empty file 
    print ('SPLITTING WORD/MASK LIST')
    print (path)
    with open (path, 'r') as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            mask = line.strip('\n')
            keyspace = calculate_keyspace(mask)
            small_keyspace_total += keyspace
            if small_keyspace_total > limit_small_keyspace:
                break
            else:
                small_ls.append(line)
        last_index = index
        if last_index != len(lines) - 1:
            for index, line in enumerate(lines):
                if index < last_index:
                    continue  
                mask = line.strip('\n')
                keyspace = calculate_keyspace(mask)
                big_keyspace_total += keyspace
                if big_keyspace_total > limit_big_keyspace:
                    break
                else:
                    big_ls.append(line)
        else: 
            big_keyspace_total = 0
            big_ls.append('')
        for index, line in enumerate(lines):
            mask = line.strip('\n')
            keyspace = calculate_keyspace(mask)
            possible_keyspace += keyspace


    with open (small_path, 'w') as f:
        f.writelines(small_ls)
    with open (big_path, 'w') as f:
        f.writelines(big_ls)
    print ('------------------------------------------------------------------------------------------------')
    print ('POSSIBLE MASK LIST KEY SPACE')
    print (possible_keyspace)
    print ('SMALL MASK LIST KEY SPACE')
    print (small_keyspace_total)
    print ('BIG MASK LIST KEY SPACE')
    print (big_keyspace_total)
    print ('SMALL MASK LIST path')
    print (small_path)
    print ('BIG MASK LIST path')
    print (big_path)
    return small_path, big_path

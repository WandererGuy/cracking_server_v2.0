import os 
date = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
  '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
      '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']


month = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
  '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
    '11', '12']

year = [str(i)for i in range (1900, 2100)]
sub_year = [str(i)[2:] for i in range (1900, 2100)]
teen = []
for i in range (2000, 2100):
    item = str(i)
    new = item[0] + 'k' + item[2:]
    teen.append(new)
for i in ('2k','2k1', '2k2', '2k3', '2k4', '2k5', '2k6', '2k7', '2k8', '2k9'):
    teen.append(i)
year.extend(sub_year)
year.extend(teen)
import itertools

import time 
def all_combo(nested_lst):

    # Get all possible permutations of the numbers
    combinations = list(itertools.product(*nested_lst))
    # Print each possible number created by permutations
    # for perm in combinations:
    #     # Convert tuple to an integer number
    #     number = str(''.join(map(str, perm)))
    return combinations
    
# print ('--------------------')
# print ([date])
# print ([month])
# print ([year])
# print ('--------------------')
# all_combo([date, month])
# print ('--------------------')
# all_combo([month, year])
# print ('--------------------')
# all_combo([date, year])
# print ('--------------------')
# all_combo([date, month, year])
tmp = []
tmp.extend(date)
tmp.extend(month)
tmp.extend(year)
tmp.extend(all_combo([date, month]))
tmp.extend(all_combo([date, year]))
tmp.extend(all_combo([month, year]))
tmp.extend(all_combo([date, month, year]))
new_tmp = set(tmp)
with open ('date.txt', 'w') as f:
    for item in new_tmp:
        number_1 = str(''.join(map(str, item)))
        number_2 = str('-'.join(map(str, item)))
        number_3 = str('/'.join(map(str, item)))
        number_4 = str(' '.join(map(str, item)))
        number_5 = str('.'.join(map(str, item)))
        f.write(f'{number_1}\n{number_2}\n{number_3}\n{number_4}\n{number_5}\n')
# def generate_date_month_year():


# path = ''
# with open('wpa-top4800.txt', 'r') as f:

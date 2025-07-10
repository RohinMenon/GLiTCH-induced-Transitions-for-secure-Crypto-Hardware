import os
import re
import argparse
# import numpy as np
#------------------

my_parser = argparse.ArgumentParser(description='Pre-silicon power side-channel analysis using PLAN')

# adding the arguments
my_parser.add_argument('ResultFolder',
                        metavar='res_folder',
                        type=str,
                        help='folder name of processed leaks')
args = my_parser.parse_args()
filePath = args.ResultFolder
fileName = filePath.split('/')[-1]

dict ={}

with open (fileName+"_leaks.txt","r") as rf:
    data_leaks = rf.read().split('\n')
    for line_leaks in data_leaks:
        info_leaks = re.match(r"(?P<val>\d+.\d+)\s+(?P<signame>.+)",line_leaks)
        if not info_leaks:
            continue
        else:
            info_leaks=info_leaks.groupdict()
# Adding the signames and its values as an array
        # if not info_leaks['signame'] in dict:
        #     dict[info_leaks['signame']]= [info_leaks['val']]
        # else:
        #     dict[info_leaks['signame']].append(info_leaks["val"])


## Straight forward dictionary implementation
        dict[info_leaks["signame"]] = info_leaks["val"]
# print("dict ",dict)
f=open(fileName+"_final_leaks.txt","w")
for key in dict:
    f.write(f"{dict[key]}\t\t{key}\n")
print("completed")
#------------------
import os
import re
from tqdm import tqdm
import operator
import argparse
import numpy as np
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
count = 0
# Iterate directory
for path in os.listdir(filePath):
    # check if current path is a file
    if os.path.isfile(os.path.join(filePath, path)):
        count += 1
print('File count:', count)

wf = open(fileName+'_leaks.txt','w')

l={}
rfiles=os.listdir(filePath)
# for i in range(0,(count)):
    # with open (filePath+f"/leaks{i}"+".txt","r") as f:
for i in tqdm(rfiles,desc="Processing Leak Files",total=len(rfiles)):
    with open(filePath+f"/{i}") as f:
        # print("i",i)
        data=f.read().split('\n')
        for line in data:
            info = re.match(r"(?P<signame>.+),(?P<val>\d+.\d+)",line)
            if not info:
                continue
            else:
                info = info.groupdict()
            # if (info['val']=='0.0000'):
            #     continue
            # else:
                # wf.write(f"{info['val']:<10}\t\t{info['signame']:>20}\n")
            if (info['signame'] in l):
                l[info['signame']].append(info['val'])
            else:
                l[info['signame']]=[info['val']]
l = dict(sorted(l.items(), key=lambda x: max(x[1]), reverse=True))


for data in tqdm(l,desc="Printing Leaks",total=len(l)):
    
    #To print only the max value of the signal
    wf.write(str(max(l[data]))+"\t\t"+data+"\n")

#     # Print all the values in array
#     wf.write(f"{l[data]}\t\t{data:>20}\n")

# print(l)

# To print the variance of signals
# l_arr={}
# for data in l:
#     fp_val=[float(x) for x in (l[data])]
#     #creating numpy array
#     np_arr=np.array(fp_val)
#     l_arr[data]=np.var(np_arr)

# for data in tqdm(l_arr,desc="Printing Variance of signals",total=len(l)):
    
#     #To print only the var value of the signal
#     wf.write(str(l_arr[data])+"\t\t"+f"{data:>50}"+"\n")


#------------------------------------------------------------------------------------------------------#
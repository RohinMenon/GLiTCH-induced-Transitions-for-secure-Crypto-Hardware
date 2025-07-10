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

observed_modules = []
occ = {}
svf_sum = {}
fin_svf ={}

with open (fileName+"_final_leaks.txt","r") as f:
    data = f.read().split('\n')
    for line in data:
        info = re.match(r"(?P<val>\d+.\d+)\s+(?P<signame>.+)",line)
        if not info:
            continue
        else:
            info = info.groupdict()
        sig_heir = info['signame'].split(".")
        for modules in sig_heir[:-1]:
          if not modules in observed_modules:
            observed_modules.append(modules)
        #No of occurance of each module
        for modu in observed_modules:
          if modu in info['signame']:
            if modu in occ:
              svf_sum[modu]+=float(info["val"])
              occ[modu]+=1
            else:
              svf_sum[modu]=float(info["val"])
              occ[modu]=1

for modu in occ:
  fin_svf[modu]=(svf_sum[modu])/(occ[modu])


with open (fileName+"_final_report.txt","w") as f:
    for modules in fin_svf:
        f.write(f"{modules:<40} = {fin_svf[modules]:<10}\n")

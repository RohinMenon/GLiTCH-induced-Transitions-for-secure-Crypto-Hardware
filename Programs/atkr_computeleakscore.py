#!/usr/bin/python3
import os
import sys
import subprocess
import numpy as np
from vcd_toggle import get_gateorder,get_transcount 
from scipy.stats import pearsonr
import math

# Checking input arguments
if(len(sys.argv)!=6):
    print(f"Error: Missing input arguments\nHelp: {sys.argv[0]} [NAME: str] [inputbits: int] [startvectorno: Int] [endvectorno: Int] [computedir: Str]")
    sys.exit(0)


# Initialize constants
try:
    NAME = sys.argv[1]
    INPUTBITS = int(sys.argv[2])
    START = int(sys.argv[3])
    END   = int(sys.argv[4])
    COM_DIR   = f"vcdgen{sys.argv[5]}"
except ValueError:
    print(f"Error: Input arguments should be integer\nHelp: {sys.argv[0]} [NAME: str] [inputbits: int] [startvectorno: Int] [endvectorno: Int] [computedir: Str]")
    sys.exit(0)


# Set the path to the testsbox.v file
# testsbox_path = "/home/ee18s050/cadence/digital_design/synthesis_4/arvindtkr/vcdGenaration/{NAME}_vcd_tb.v"
# sdf_cmd_path = f"../{NET_DIR}/SBOX_results/SBOX.sdf.X"
# os.system(f"cp {testsbox_path} .")
# os.system(f"cp {sdf_cmd_path} .")

#KEY = int(2**INPUTBITS)-1
KEY = 100
circuit_genus_file = f"/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/{NAME}/{NAME}_genus.txt"
os.makedirs(COM_DIR, exist_ok=True)
os.chdir(COM_DIR)


# Remove existing directories and files
os.system("rm -fr leakfile INCA_libs")


# Required variables
gate_dict = get_gateorder(circuit_genus_file)
leakdict = {}
runs = END-START+1
toggle_array = np.zeros(shape=(len(gate_dict),runs),dtype=int)
oracle_array = np.zeros(shape=(runs),dtype=int)
score_array  = np.zeros(shape=(len(gate_dict)),dtype=float)


# Perform simulations
for i in range(1, runs + 1):
    actual_i = (i+START-1)
    multiplier = 37
    init = (actual_i*multiplier) // (2**INPUTBITS)
    excit = (actual_i*multiplier) % (2**INPUTBITS)
    print(f"********* Info : Running {i} of {runs} iteration {init} -> {excit} ***********")

    
    os.system(f"mv ../saif/{KEY}_{actual_i}.saif .")       
    
    # Store variable values for oracle computation file
    HD_Oracle = bin(init^excit).count('1')
    # Get toggle from the current computation of saif
    toggle_array[:,i-1] = get_transcount(gate_dict,f"{KEY}_{actual_i}.saif")
    oracle_array[i-1] = HD_Oracle

    os.system(f"mv {KEY}_{actual_i}.saif ../saif")

for node in gate_dict.keys():
    score = pearsonr(oracle_array,toggle_array[gate_dict[node],:])[0]
    score = 0 if(math.isnan(score)) else np.abs(score)
    leakdict[node] = score
    #print(node,oracle_array,toggle_array[gate_dict[node],:],score)

# sorting the leakdict
leakdict = dict(sorted(leakdict.items(), key=lambda item: item[1], reverse=True))

leakfile = f"../{NAME}_leakscore.txt"

with open(leakfile, "w") as txtfile:
    for node in leakdict.keys():
        txtfile.write(f"{node},{round(leakdict[node],4)}\n")
txtfile.close()
print("Info: Leak score produced in ",leakfile)

os.chdir("..")

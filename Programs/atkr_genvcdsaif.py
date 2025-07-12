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
    print(f"Error: Input arguments should be integer\nHelp: {sys.argv[0]} [NAME: str] [inputbits: int] [startvectorno: Int] [endvectorno: Int] [computedir: Str] ")
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

#KEY = int(2**INPUTBITS)-1
KEY = 100
circuit_genus_file = "/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/{NAME}/{NAME}_genus.txt"

# Set the path to the testsbox.v file
# testsbox_path = "/home/ee18s050/cadence/digital_design/synthesis_4/arvindtkr/vcdGenaration/{NAME}_vcd_tb.v"
# sdf_cmd_path = f"../{NET_DIR}/SBOX_results/SBOX.sdf.X"
# os.system(f"cp {testsbox_path} .")
# os.system(f"cp {sdf_cmd_path} .")

# Create the saif/vcdgenTest directory
os.makedirs("saif", exist_ok=True)
os.makedirs(COM_DIR, exist_ok=True)
os.chdir(COM_DIR)
os.system(f"cp ../{NAME}* .")


# Remove existing directories and files
os.system("rm -fr leakfile INCA_libs")

runs = END-START+1


# Perform simulations
for i in range(1, runs + 1):
    actual_i = (i+START-1)
    multiplier = 37
    init = (actual_i*multiplier) // (2**INPUTBITS)
    excit = (actual_i*multiplier) % (2**INPUTBITS)
    print(f"********* Info : Running {i} of {runs} iteration {init} -> {excit} ***********")
    
    

    # Modify testsbox.v
    command_1 = f"sed -i 's/  	k=.*/  	k={KEY}\;/;  s/  	\\$dumpfile.*/  	\\$dumpfile(\"{KEY}_{actual_i}.vcd\")\;/; s/  	in=.*/  	in={init}\;/; s/  	#2 in=.*/  	#2 in={excit}\;/' {NAME}_vcd_tb.v"
    args = [command_1]
    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    output,error = popen.communicate()

    # Run behavioral simulation
    command_2 = f"xrun  -quiet -append_log -access  +rwc  -v93 -l ./xrun_logs/xrun ../../new_verilog_{NAME}_*.v ../../{NAME}_results/{NAME}_netlist.v {NAME}_vcd_tb.v  -sdf_no_warnings -sdf_verbose -sdf_cmd_file ../../{NAME}_results/sdf_cmd -top {NAME}_tb"
    # command_2 = f"xrun  -quiet -append_log -access  +rwc  -v93 -l ./xrun_logs/xrun ../../new_verilog_{NAME}_*.v ../../{NAME}_results/{NAME}_netlist.v {NAME}_vcd_tb.v -top {NAME}_tb +delay_mode_zero"
    args = [command_2]
    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    output,error = popen.communicate()
    # print(output.decode("utf-8"))
    os.system(f"sleep 0.8")


    # Generate saif from vcd
    command_3 = f"../../{NAME}_results/vcd2saif -input {KEY}_{actual_i}.vcd -output {KEY}_{actual_i}.saif"
    args = [command_3]
    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    output,error = popen.communicate()
    #print(output.decode("utf-8"))
    os.system(f"rm {KEY}_{actual_i}.vcd")
    os.system(f"mv {KEY}_{actual_i}.saif ../saif")
    


print(f"Info: Saif files are created")
# Clean up
#os.system("rm -fr SBOX.sdf.X sdf.log xcelium.d xrun_logs")
os.chdir("..")

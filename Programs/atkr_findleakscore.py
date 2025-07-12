#!/usr/bin/python3
import os
import sys
import shutil
import subprocess
import numpy as np
from vcd_toggle import get_gateorder,get_transcount 
from scipy.stats import pearsonr
import math


def findleakscore(circuit_name,path_final,circuit_files_directory,typex,start_vectorcount=0,end_vectorcount=2000,KEY=100):
    	
	# Set the path to the {circuit_name}_vcd_tb.v file
    path_final_type = path_final+"/"+typex
    vcd_testbench_file = f"{circuit_files_directory}/{circuit_name}/{circuit_name}_vcd_tb.v"
    sdf_cmd_file = f"{path_final_type}/{circuit_name}_results/{circuit_name}.sdf.X"
	
	# Create the saif/vcdgenTest directory
    leakscore_dir = f"{path_final_type}/{circuit_name}_leakscore" 
    os.makedirs(leakscore_dir,exist_ok=True)
	
	
	# Copy {circuit_name}_vcd_tb.v to the current directory
    shutil.copy2(vcd_testbench_file,leakscore_dir)
    shutil.copy2(sdf_cmd_file,leakscore_dir)
	
	# Required variables
    gate_dict = get_gateorder(f"{circuit_files_directory}/{circuit_name}/{circuit_name}_genus.txt")
    leakdict = {}
    runs = end_vectorcount-start_vectorcount+1
    toggle_array = np.zeros(shape=(len(gate_dict),runs),dtype=int)
    oracle_array = np.zeros(shape=(runs),dtype=int)
    score_array  = np.zeros(shape=(len(gate_dict)),dtype=float)
	
	
	# Perform simulations
    for i in range(1, runs + 1):
        actual_i = (i+start_vectorcount-1)
        init = actual_i // 256
        excit = actual_i % 256
        print(f"********* Info : Running {i} of {runs} iteration {init} -> {excit} ***********")
	
	    
	
	    # Modify {circuit_name}_vcd_tb.v
        command_1 = f"sed -i 's/  	k=.*/  	k={KEY}\;/;  s/  	\\$dumpfile.*/  	\\$dumpfile(\"{KEY}_{actual_i}.vcd\")\;/; s/  	in=.*/  	in={init}\;/; s/  	#2 in=.*/  	#2 in={excit}\;/' {circuit_name}_vcd_tb.v"
        args = [command_1]
        popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,cwd=leakscore_dir)
        output,error = popen.communicate()
	
	
	    # Run behavioral simulation
        command_2 = f"xrun  -quiet -append_log -access  +rwc  -v93 -l ./xrun_logs/xrun ../new_verilog_{circuit_name}_*.v ../{circuit_name}_results/{circuit_name}_netlist.v {circuit_name}_vcd_tb.v -sdf_no_warnings -sdf_verbose -sdf_cmd_file ../{circuit_name}_results/sdf_cmd -top testsbox"
	    # command_2 = f"xrun  -quiet -append_log -access  +rwc  -v93 -l ./xrun_logs/xrun ../{type_AmorGm}/new_verilog_SBOX_*.v ../{type_AmorGm}/SBOX_results/SBOX_netlist.v {circuit_name}_vcd_tb.v -top testsbox +delay_mode_zero"
        args = [command_2]
        popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,cwd=leakscore_dir)
        output,error = popen.communicate()
        print(output.decode("utf-8"))
        os.system(f"sleep 0.8")
	
	
	    # Generate saif from vcd
        command_3 = f"../{circuit_name}_results/vcd2saif -input {KEY}_{actual_i}.vcd -output {KEY}_{actual_i}.saif"
        args = [command_3]
        popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,cwd=leakscore_dir)
        output,error = popen.communicate()
	    #print(output.decode("utf-8"))
	
	    # Store variable values for oracle computation file
        HD_Oracle = bin(init^excit).count('1')
	    
	
	    # Get toggle from the current computation of saif
        toggle_array[:,i-1] = get_transcount(gate_dict,f"{leakscore_dir}/{KEY}_{actual_i}.saif")
        oracle_array[i-1] = HD_Oracle
        os.system(f"rm {leakscore_dir}/{KEY}_{actual_i}.*")
	    
	
	# computing the PearsonR factor
    for node in gate_dict.keys():
        score = pearsonr(oracle_array,toggle_array[gate_dict[node],:])[0]
        score = 0 if(math.isnan(score)) else np.abs(score)
        leakdict[node] = score
	    #print(node,oracle_array,toggle_array[gate_dict[node],:],score)
	
	# sorting the leakdict
    leakdict = dict(sorted(leakdict.items(), key=lambda item: item[1], reverse=True))
	
    file = f"{leakscore_dir}/{circuit_name}_{typex}_leakscore.txt"
	
    with open("leakfile", "w") as txtfile:
        for node in leakdict.keys():
            txtfile.write(f"{node},{round(leakdict[node],4)}\n")
    txtfile.close()
    print("Info: Leak score produced in ",file)

def findleakscore_GM(circuit_name,path_final,circuit_files_directory,typex,start_vectorcount=0,end_vectorcount=2000,KEY=100):
    	
	# Set the path to the {circuit_name}_vcd_tb.v file
    path_final_type = path_final+"/"+typex
    vcd_testbench_file = f"{circuit_files_directory}/{circuit_name}/{circuit_name}_vcd_tb.v"
    sdf_cmd_file = f"{path_final_type}/{circuit_name}_results/{circuit_name}.sdf.X"
	
	# Create the saif/vcdgenTest directory
    leakscore_dir = f"{path_final_type}/{circuit_name}_leakscore" 
    os.makedirs(leakscore_dir,exist_ok=True)
	
	
	# Copy {circuit_name}_vcd_tb.v to the current directory
    shutil.copy2(vcd_testbench_file,leakscore_dir)
    shutil.copy2(sdf_cmd_file,leakscore_dir)
	
	# Required variables
    gate_dict = get_gateorder(f"{circuit_files_directory}/{circuit_name}/{circuit_name}_genus.txt")
    leakdict = {}
    runs = end_vectorcount-start_vectorcount+1
    toggle_array = np.zeros(shape=(len(gate_dict),runs),dtype=int)
    oracle_array = np.zeros(shape=(runs),dtype=int)
    score_array  = np.zeros(shape=(len(gate_dict)),dtype=float)
	
	
	# Perform simulations
    for i in range(1, runs + 1):
        actual_i = (i+start_vectorcount-1)
        init = actual_i // 256
        excit = actual_i % 256
        print(f"********* Info : Running {i} of {runs} iteration {init} -> {excit} ***********")
	
	    
        '''	
	    # Modify {circuit_name}_vcd_tb.v
        command_1 = f"sed -i 's/  	k=.*/  	k={KEY}\;/;  s/  	\\$dumpfile.*/  	\\$dumpfile(\"{KEY}_{actual_i}.vcd\")\;/; s/  	in=.*/  	in={init}\;/; s/  	#2 in=.*/  	#2 in={excit}\;/' {circuit_name}_vcd_tb.v"
        args = [command_1]
        popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,cwd=leakscore_dir)
        output,error = popen.communicate()
	
	
	    # Run behavioral simulation
        command_2 = f"xrun  -quiet -append_log -access  +rwc  -v93 -l ./xrun_logs/xrun ../new_verilog_{circuit_name}_*.v ../{circuit_name}_results/{circuit_name}_netlist.v {circuit_name}_vcd_tb.v -sdf_no_warnings -sdf_verbose -sdf_cmd_file ../{circuit_name}_results/sdf_cmd -top testsbox"
	    # command_2 = f"xrun  -quiet -append_log -access  +rwc  -v93 -l ./xrun_logs/xrun ../{type_AmorGm}/new_verilog_SBOX_*.v ../{type_AmorGm}/SBOX_results/SBOX_netlist.v {circuit_name}_vcd_tb.v -top testsbox +delay_mode_zero"
        args = [command_2]
        popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,cwd=leakscore_dir)
        output,error = popen.communicate()
        print(output.decode("utf-8"))
        os.system(f"sleep 0.8")
	
	
	    # Generate saif from vcd
        command_3 = f"../{circuit_name}_results/vcd2saif -input {KEY}_{actual_i}.vcd -output {KEY}_{actual_i}.saif"
        args = [command_3]
        popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,cwd=leakscore_dir)
        output,error = popen.communicate()
	    #print(output.decode("utf-8"))
	    '''
	    # Store variable values for oracle computation file
        HD_Oracle = bin(init^excit).count('1')
	    
	
	    # Get toggle from the current computation of saif
        toggle_array[:,i-1] = get_transcount(gate_dict,f"{leakscore_dir}/saif/{KEY}_{actual_i}.saif")
        oracle_array[i-1] = HD_Oracle
        #os.system(f"rm {leakscore_dir}/saif/{KEY}_{actual_i}.*")
	    
	
	# computing the PearsonR factor
    for node in gate_dict.keys():
        score = pearsonr(oracle_array,toggle_array[gate_dict[node],:])[0]
        score = 0 if(math.isnan(score)) else np.abs(score)
        leakdict[node] = score
	    #print(node,oracle_array,toggle_array[gate_dict[node],:],score)
	
	# sorting the leakdict
    leakdict = dict(sorted(leakdict.items(), key=lambda item: item[1], reverse=True))
	
    file = f"{leakscore_dir}/{circuit_name}_{typex}_leakscore.txt"
	
    with open("leakfile", "w") as txtfile:
        for node in leakdict.keys():
            txtfile.write(f"{node},{round(leakdict[node],4)}\n")
    txtfile.close()
    print("Info: Leak score produced in ",file)

if __name__ == "__main__":
    circuit_name = "SBOX"
    path_final = sys.argv[1]
    typex = sys.argv[2]
    #path_final = path_final = os.path.join(simulation_results_directory,circuit_name,run_name)
    circuit_files_directory = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','circuit_files')
    findleakscore_GM(circuit_name,path_final,circuit_files_directory,typex,start_vectorcount=0,end_vectorcount=1700,KEY=100)


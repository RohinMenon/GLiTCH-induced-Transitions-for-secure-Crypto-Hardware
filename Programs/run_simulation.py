import subprocess
import shutil
import transition_count_2 #TODO:fix
import numpy as np
import re

def run_simulation(circuit_name,run_number,auxillary_files_directory,circuit_files_directory,path_final,csv_format_array):
    print(f'Info: run_simulation(): Synthesizing {circuit_name}')
    circuit_files_path = circuit_files_directory + '/' + circuit_name
    run_number_string = str(run_number)
    csv_format_local_array = np.zeros(shape=(7),dtype = object)

    #'''
    shutil.copy2(auxillary_files_directory + "/all_in_one_sizes_1.sh", path_final)
    shutil.copy2(auxillary_files_directory + "/all_in_one_sizes_2.sh", path_final)
    files_to_copy_1 = ["rc_new.tcl","start_genus_1.sh","start_genus_2.sh","power.tcl"]

    for f in files_to_copy_1:
        shutil.copy2(auxillary_files_directory + '/' + f, path_final)
        
    #replacing the desitinaion path in all copied files
    command_1 = f"sed -i -e 's,dest=\"\",dest=\"{path_final}\",' {path_final}/all_in_one_sizes_1.sh {path_final}/start_genus_1.sh {path_final}/start_genus_2.sh {path_final}/all_in_one_sizes_2.sh"

    args = [command_1]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    popen.wait()

    #set circuitname and runname
    command_1a = f"sed -i -e 's,circuit=\"\",circuit=\"{circuit_name}\",' -e 's,run_name=\"\",run_name=\"{circuit_name}_{run_number_string}\",' {path_final}/all_in_one_sizes_1.sh {path_final}/all_in_one_sizes_2.sh"

    args = [command_1a]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    popen.wait()

    #setting the directory
    command_1b = f"sed -i -e 's,/home/ee18s050/cadence/digital_design/synthesis_2/c880_sizes85,{path_final},' {path_final}/rc_new.tcl"

    args = [command_1b]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    popen.wait()
    

    command_2 = f"\"{path_final}/all_in_one_sizes_1.sh\""

    args = [command_2]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,cwd = path_final)
    output,error = popen.communicate()
    output = output.decode("utf-8")
    #'''

    print(f'Info: run_simulation(): genus run completed.') 
    with open(path_final + f"/{circuit_name}_results/timing.rpt",'r') as f2:
        timing_report = f2.read()
    f2.close()
    with open(path_final + f"/{circuit_name}_results/gates.rpt",'r') as f3:
        area_report = f3.read()
    f3.close()
        
    critical_path_timing = int(re.findall("out port\s+\+\d+\s+(\d+)",timing_report)[0])
    max_critical_path_timing = max(csv_format_array[3],critical_path_timing)
    clock_period_in_ps= max_critical_path_timing + 100 - max_critical_path_timing % 100
    area = float(re.findall("total\s+\d+\s+(.+)\s+\d+",area_report)[0])
 
    #'''
    files_to_copy_2 = [f"{circuit_name}_tb.v",f"{circuit_name}_sdf_tb.v",f"{circuit_name}_inputs.txt"]
    for f in files_to_copy_2:
        shutil.copy2(circuit_files_path + '/' + f, path_final + '/' + circuit_name + "_results")
    files_to_copy_3 = ["vcd2saif","vcd2saif_initiate","irun_cmds.sh","sdf_cmd"]
    for f in files_to_copy_3:
        shutil.copy2(auxillary_files_directory + '/' + f, path_final + '/' + circuit_name + "_results")
    #'''
    half_clock_period_in_ns = (clock_period_in_ps / 1000) / 2
    total_run_time = clock_period_in_ps
    #''' 
    command_3 = f"sed -i -e 's/1100.55/{total_run_time}/g' -e 's/0.55/{half_clock_period_in_ns}/g' {path_final}/all_in_one_sizes_2.sh"

    args = [command_3]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    output,error = popen.communicate()

    command_3a = f"sed -i -e 's,/home/ee18s050/cadence/digital_design/synthesis_2/c880_sizes85,{path_final},g' {path_final}/{circuit_name}_results/irun_cmds.sh"

    args = [command_3a]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True)
    output,error = popen.communicate()
    print(f'Info: run_simulation(): Simulating {circuit_name}')
    #'''
    command_4 = f"\"{path_final}/all_in_one_sizes_2.sh\""

    args = [command_4]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE,shell=True,cwd = path_final)
    output,error = popen.communicate()
    output = output.decode("utf-8")
    print(f'Info: run_simulation(): {circuit_name} simulation completed.') 
    power = np.zeros(shape=(1,3))
    power_values = re.findall(f'{circuit_name}\s+\d+\s+(.*)\n',output)


    for i in range(len(power_values)):
        power[0,i] = float(power_values[i].split()[2]) / 1000


    power[0,2] = power[0,0] - power[0,1]

    netlist_file = circuit_files_path + '/' + circuit_name + '_' + 'genus.txt'
    #total_transitions,functional_transitions,no_of_glitches,glitch_count_array = transition_count.transition_count(circuit_name,netlist_file,path_final) # atkrcommented
    total_transitions,functional_transitions,total_glitches,toggle_count_array = transition_count_2.transition_count(circuit_name,netlist_file,path_final) # TODO: fix transition counts
    total_transitions= 0
    functional_transitions = 0
    total_glitches= 0 
    #toggle_count_array = 0 #TODO:Fix
    print(f'Info: run_simulation(): {circuit_name} has as {max(toggle_count_array[:,2])} Max glitch count.') #TODO: fix 
 
    glitch_power = round(power[0,2],2)
    total_power = round(power[0,0],2)
    

    csv_format_local_array[0] = critical_path_timing
    csv_format_local_array[1] = area    
    csv_format_local_array[2] = glitch_power
    csv_format_local_array[3] = total_power
    csv_format_local_array[4] = total_transitions
    csv_format_local_array[5] = functional_transitions
    csv_format_local_array[6] = total_glitches
    
    #return csv_format_local_array, glitch_count_array # atkr commented
    return csv_format_local_array, toggle_count_array # atkr modified

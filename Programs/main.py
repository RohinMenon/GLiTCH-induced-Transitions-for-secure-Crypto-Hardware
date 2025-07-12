from pylab import *
from pyparamopt import paramopt 
from timeopt import timeopt 
from area_minimum import gatesize 
from atkr_glitchOpt import glitchOptObj
from postprocessAM import postprocessAM
from postprocessGM import postprocessGM
from sdf_modifier import sdf_modify
#import parser_verilog_ver8_splcase_avg as psr
import atkr_parser_verilog_ver9 as psr
import jb_parser_verilog_ver11 as psr2
from timeopt_considering_transition_time import timeopt_considering_transition_time 
from area_minimum_considering_transition_time import gatesize_considering_transition_time 
from glitch_minimum_considering_transition_time import glminReducedObj_considering_transition_time
import round_off_function
from compare_update_leak import updateLeakCsv
from atkr_findcriticalgate import analyse_critical


############################################################

import shutil
import os
import re
import sys
import numpy as np
############################################################
import gate_name_gen as gng
#import standard_cell_verilog_parser as verilog_psr
import atkr_standard_cell_verilog_parser as verilog_psr
#import library_parser_v3_all_gates_selected as lib_psr
import atkr_library_parser_v3_all_gates_selected as lib_psr
import generate_verilog_source as gvs
############################################################

import transition_count_2 #TODO:fix
import transition_count_avg
import timing_analysis
import input_stage_info
import input_stage_info_v2
import get_glitch
import get_leaks
import temp_file_generator
import read_criticality_metric_files
import generate_library_and_netlist_files
import generate_criticality_metric_files
import run_simulation


############################################################
from inspect import getsourcefile   #### } Used to get directory of the currently run main file
from os.path import abspath         #### }


############################################################
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
np.set_printoptions(suppress = True,precision=0)
sys.setrecursionlimit(10000000)
Cref = 0.731     # Input Capacitance of Unit Inverter in pF for the standard cell library used
maxGsize = 16


############################################################
#circuits                                    = ["c17":5,"c432","c880","c1908","c2670","c3540","c5315","c6288","c7552","SBOX":8]
#circuits 									 = ["c17"]
#circuits                                    = ["SBOX"]
#circuits 									 = ["SBOX_aes"] #JB_modified
circuits 									 = ["masked_skinny_sbox"] #JB_modified
#circuits 									 = ["unmasked_present_sbox"] #JB_modified
#circuits 									 = ["unmasked_ascon5_sbox"]
#circuits 									 = ["unmasked_prince_sbox"]
#circuits 									 = ["present_encrypt"]
#circuits 									 = ["masked_and_sbox"]
#circuits 									 = ["unmasked_aes_sbox"]
#circuits 									 = ["unmasked_skinny_sbox"] #JB_modified
#circuits 									 = ["unmasked_midori_sbox"]
#circuits 									 = ["unmasked_clefia_sbox"]
#circuits 									 = ["unmasked_AES_full_sbox"]
inputbits                                    = 64
leakpath_AM 								 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/masked_present_sbox/masked_present_sbox_leakscore_1p1.txt'
#leakpath_AM                                 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/c17/c17_leakscore_1p1.txt'
#leakpath_AM                                 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/SBOX/SBOX_leakscore_1p1.txt'
#leakpath_AM							         = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/present_encrypt/present_encrypt_leakscore_1p1.txt' #JB Modified
#leakpath_AM 								 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/unmasked_aes_sbox/unmasked_aes_sbox_leakscore_1p1.txt'
#leakpath_AM 								 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/unmasked_present_sbox/unmasked_present_sbox_leakscore_1p1.txt'
#leakpath_AM 							 	 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/unmasked_ascon5_sbox/unmasked_ascon5_sbox_leakscore_1p1.txt'
#leakpath_AM 								 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/unmasked_prince_sbox/unmasked_prince_sbox_leakscore_1p1.txt'
#leakpath_AM 								 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/unmasked_skinny_sbox/unmasked_skinny_sbox_leakscore_1p1.txt'
#leakpath_AM 								 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/unmasked_midori_sbox/unmasked_midori_sbox_leakscore_1p1.txt'
#leakpath_AM 								 = '/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/unmasked_SM4_sbox/unmasked_SM4_sbox_leakscore_1p1.txt'

twall_to_be_run                             = [1.1]
excessP_list                                = [1.35]
noOfGatesToConstraint_list                  = [20]
#notes_to_print                              = 'Just N  MAX with max constraints'
#notes_to_print                              = 'Just MIN (2/3)N  without 0 deltaleak with min cnst'
notes_to_print                              = 'FIRST N GATES to MINIMISE OR MAXIMISE (min constraint)'


############################################################
#available_round_off_options                 = ["no_round_off","half_integer_sizes","integer_sizes","library_sizes"]
available_round_off_options                 = ["no_round_off"] #TODO: Check for lib sizes
inertial_delay_fraction_list                = [1]
glitchExponent                              = 2.0
downsizing                                  = False
average_delay_simulation                    = True
dont_consider_transition_time               = True
use_default_critical_files                  = True
use_leakdata                                = True
downsizing_timing_relaxation_percentage     = 0


############################################################
programs_path_including_file_name = abspath(getsourcefile(lambda:0))            ## Not needed, can be removed
programs_path_directory = os.path.dirname(programs_path_including_file_name)    ## Not needed, can be removed
circuit_files_directory = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','circuit_files')
simulation_results_directory = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','simulation_results')
auxillary_files_directory = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','auxillary_files')
verilog_input_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','techfiles2', 'fsf0l_ers_generic_core_30.v')
library_input_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','techfiles2','fsf0l_ers_generic_core_tt1p2v25c.lib')
criticality_files_path = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','circuit_files')

############################################################
print(f'Info: main(): Starting the program for optimization')
print(f'NOTE: main(): {notes_to_print}')
print("#---------------------------------------------------------#") 
print(f'Info: main(): circuits are {circuits}')
print(f'Info: main(): twallfrac are {twall_to_be_run}')
print(f'Info: main(): areafrac is {excessP_list}')
print(f'Info: main(): using external thresholding {use_leakdata}')
print(f'Info: main(): number of gates to constraint {noOfGatesToConstraint_list}')
print(f'Info: main(): glitchExponent is {glitchExponent}')
print(f'Info: main(): inertialdelayfrac is {inertial_delay_fraction_list}')
print("#---------------------------------------------------------#\n\n") 


for noOfGatesToConstraint in noOfGatesToConstraint_list:
    for circuit_name in circuits:
    
        print(f"#--------------- {circuit_name}: Starting run with {noOfGatesToConstraint} gates to constraints ---------------#")
    
        netlist_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','circuit_files',circuit_name,f'{circuit_name}_genus.txt')
        leakpath_notiming = f"{circuit_files_directory}/{circuit_name}/{circuit_name}_leakscore_notiming.txt"
        
        if not os.path.exists(os.path.join(simulation_results_directory,circuit_name)):
            os.makedirs(os.path.join(simulation_results_directory,circuit_name))

        print(f'Info: main(): Parsing file for {circuit_name}_genus.txt')
        #F_in, Opsize_in, Gate_logical_effort_in, fan_in_list_in, parasitic_delay_in, gate_output_wire_capacitance_in,\
        #level_of_gate_inputs_in, primary_gates_type_list, no_of_primary_gates,gate_type_list,out_list,in_out_list,gate_name = psr.parser(circuit_files_directory,circuit_name)   # Parser, used for generating the F matrix from
        F_in, Opsize_in, Gate_logical_effort_in, fan_in_list_in, parasitic_delay_in, gate_output_wire_capacitance_in,\
        level_of_gate_inputs_in, primary_gates_type_list, no_of_primary_gates,gate_type_list,out_list,in_out_list,gate_name = psr2.parser(circuit_files_directory,circuit_name)   # Parser, used for generating the F matrix from    
        #print(gate_type_list)
        #print(gate_name)
        #print(level_of_gate_inputs_in)
        #input_stage_data = input_stage_info_v2.input_stage_info_v2(os.path.join(circuit_files_directory,circuit_name,circuit_name + "_genus.txt")) #TODO: fix
        print(f'Info: main(): Input stage data collected (No Idea)')
        F,Opsize,Glog,N,Iparr,Ips,maxIp,parasiticDelay,gate_output_wire_capacitance = paramopt(F_in,Opsize_in,Gate_logical_effort_in,fan_in_list_in.values(),parasitic_delay_in,gate_output_wire_capacitance_in)
        primarygates = [1 if 0 in level_of_gate_inputs_in[i] else 0 for i in range(N)]
        if (dont_consider_transition_time == True):
            T0,indIparr = timeopt(N,F,Opsize,Glog,Iparr,Ips,maxIp,parasiticDelay,gate_output_wire_capacitance,Cref,dont_consider_transition_time)   # Gets the timing wall for the circuit
            print(f'Info: main(): Without considering Transition timing TWall is {T0}')
        else:
            T0,indIparr = timeopt_considering_transition_time(N,F,Opsize,Glog,Iparr,Ips,maxIp,parasiticDelay,gate_output_wire_capacitance,Cref)
            print(f'Info: main(): With considering Transition timing TWall is {T0}')
        primary_gates_details = np.zeros(shape=(no_of_primary_gates,3),dtype=object)
        primary_gates_type_list_reshaped = primary_gates_type_list.reshape(no_of_primary_gates)
        primary_gates_details[:,0] = primary_gates_type_list_reshaped
        for twall_count, twall in enumerate(twall_to_be_run):
            for inertial_delay_count,inertial_delay_frac in enumerate(inertial_delay_fraction_list):
                print(f"\nInfo: main(): {circuit_name}: Computing at {twall}*T0  with {inertial_delay_frac} as inertialdelayfraction")
                if (dont_consider_transition_time == True):
                    csv_format_array = np.zeros(shape=(30),dtype = object)
                    comparison = np.zeros(shape = (N,18),dtype = object)
                    glitch_count_array = np.zeros(shape=(N,1))
                    print(f'Info: main(): Starting Area minimisation GP') 
                    AMsol,primary_gates_AM_sizes = gatesize(N,T0,F,Opsize,Glog,Iparr,indIparr,Ips,maxIp,parasiticDelay,gate_output_wire_capacitance,Cref,dont_consider_transition_time,Twall=twall)   # Sets up area minimization using GPkit
                    print(f'Info: main(): after area_minimation fracxTwall allowed is {twall*T0} and Timing obtained is {AMsol["variables"]["Ts"]}')
                    print(f'Info: main(): after area_minization area obtained is {sum(AMsol["variables"]["x"])}')
                    #print(f'Info: main(): primary_gates_AM_sizes are {primary_gates_AM_sizes}')
                    print(f'Info: main(): Area Minisation gpkit completed')
                    if(AMsol != None):
                        AMsizes = AMsol["variables"]["x"]
                    #print(AMsol)
                    for excessP_count,excessP in enumerate(excessP_list):
                       for round_off_count,round_off_option in enumerate(available_round_off_options):
                           print(f'\nInfo: main(): Running with areafrac as {excessP} for the generated Area minimum sizes')
                           list_of_folders = next(os.walk(os.path.join(simulation_results_directory,circuit_name)))[1]
                           circuit_name_folders = [x for x in list_of_folders if x.startswith(circuit_name)]
                           circuit_file_numbers = [x.group(1) for x in (re.search(f"{circuit_name}_(.+)",folder) for folder in list_of_folders) if x]
                           circuit_file_numbers_sorted = sorted(circuit_file_numbers,key=int)
                           if(circuit_file_numbers_sorted):
                               run_count = int(circuit_file_numbers_sorted[-1])
                           else:
                               run_count = 0
                           run_number = run_count + 1
                           run_name = circuit_name + '_' + str(run_number)
                           path_final = os.path.join(simulation_results_directory,circuit_name,run_name)
                           if not os.path.exists(path_final):
                               os.makedirs(path_final)
                               print("Info: main():",path_final, "created")
                           else:
                               print("Info: main():", path_final, "already exists")
                           path_final_AM = os.path.join(path_final,'AM')
                           if not os.path.exists(path_final_AM):
                               os.makedirs(path_final_AM)
                           np.savetxt(path_final_AM + "/AMsizes.txt",AMsizes)
                           AMsizes = round_off_function.round_off_fn(round_off_option,AMsizes) # Rounds off the obtained real valued solution based on the contents of the 'round_off_option' variable
                           verilog_destination_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','simulation_results',circuit_name,run_name,'AM', 'new_verilog_' + run_name + '.v')
                           library_destination_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','simulation_results',circuit_name,run_name,'AM', 'new_lib_' + run_name + '.lib')
                           source_verilog_write_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','simulation_results',circuit_name,run_name,'AM', 'new_verilog_source_' + run_name + '.v')
                           run_mode="AM"
                           generate_library_and_netlist_files.generate_library_and_netlist_files(run_mode,path_final_AM,netlist_file,source_verilog_write_file,verilog_input_file,verilog_destination_file,library_input_file,library_destination_file)     ## Completed. Generates the library files for the obtained AM sizes
                           print("Info: main(): Written library files and verilog files in ",path_final_AM) 
                           #timing,area,glitch_power,total_power,notiming_transition,timing_tranition,glitches = csv_format_local_array_AM
                           #toggle_count_array = [notiming toggle, timing toggle, glitch in each gate] 
                           csv_format_local_array_AM,toggle_count_array_AM = run_simulation.run_simulation(circuit_name,run_number,auxillary_files_directory,circuit_files_directory,path_final_AM,csv_format_array) # atkr modified
                           #print(toggle_count_array_AM)
                           csv_format_array[[3,8,10,12,20,22,24]] = csv_format_local_array_AM
                           #comparison[:,2] = glitch_count_array_AM # atkr commented 
                           #comparison[:,2] = toggle_count_array_AM[:,2] # atkr modified TODO:fix
                           #print(toggle_count_array_AM)
   						   
                           print("\n#------------------- AREA MINIMIZATION SUMMARY -----------------------#")
                           print(f'Info: summary: circuit_name {circuit_name}')
                           print(f'Info: summary: Tfrac_set {twall}')
                           print(f'Info: summary: Twall {T0}')
                           print(f'Info: summary: Timing_obtained {AMsol["variables"]["Ts"]}')
                           print(f'Info: summary: Tfrac_obtained {round(AMsol["variables"]["Ts"]/T0,2)}')
                           print(f'Info: summary: Awall {sum(AMsol["variables"]["x"])}')
                           #-------------------------------------------------------------------------------------------#
                           # logging into summary 
                           #-------------------------------------------------------------------------------------------#
                           summaryhandler = open(path_final+"/AM_summary.txt",'w')
                           summaryhandler.write("\n#------------------- AREA MINIMIZATION SUMMARY -----------------------#\n")
                           summaryhandler.write(f'Info: summary: circuit_name {circuit_name}\n') 
                           summaryhandler.write(f'Info: summary: Tfrac_set {twall}\n') 
                           summaryhandler.write(f'Info: summary: Twall {T0}\n') 
                           summaryhandler.write(f'Info: summary: Timing_obtained {AMsol["variables"]["Ts"]}\n') 
                           summaryhandler.write(f'Info: summary: Tfrac_obtained {round(AMsol["variables"]["Ts"]/T0,2)}\n') 
                           summaryhandler.write(f'Info: summary: Awall {sum(AMsol["variables"]["x"])}\n')
                           summaryhandler.close()
                           #print(f'Info: main(): csv_format_local_array_AM = {csv_format_local_array_AM} and csv_format_array = {csv_format_array}')
                           #print(f'Info: main(): primary_gates_details = {primary_gates_details} ')
                           print("Info: main(): Area minimization logic Complete")
                           # atkr modified finding temporary leak score
                           vcd_testbench_file = f"{circuit_files_directory}/{circuit_name}/{circuit_name}_vcd_tb.v"
                           sdf_cmd_file = f"{path_final_AM}/{circuit_name}_results/{circuit_name}.sdf.X"
                           leakscore_dir = f"{path_final_AM}/{circuit_name}_leakscore/" 
                           os.makedirs(leakscore_dir,exist_ok=True)
                           #shutil.copy2(vcd_testbench_file,leakscore_dir) #TODO: fix
                           #shutil.copy2(sdf_cmd_file,leakscore_dir) #TODO:fix
                           #findleakscore(circuit_name,path_final,circuit_files_directory,"AM",0,2000,100)
                           primary_gates_details[:,1] = primary_gates_AM_sizes
                           if (use_default_critical_files):
                               syn_criticality_file_path = os.path.join(criticality_files_path,circuit_name,circuit_name + '_' + 'SynCriticality' + '.txt')
                               out_criticality_file_path = os.path.join(criticality_files_path,circuit_name,circuit_name + '_' + 'out' + '.txt')
                           else:
                               generate_criticality_metric_files.critical_file_generation()     # To be completed
                               syn_criticality_file_path = os.path.join(criticality_files_path,circuit_name + '_' + run_number,circuit_name + '_' + 'SynCriticality' + '.txt')
                               out_criticality_file_path = os.path.join(criticality_files_path,circuit_name + '_' + run_number,circuit_name + '_' + 'out' + '.txt')
                           #---------------- Not Using Yet -------------------# 
                           # criticality = criticality_array_from_matric
                           # glitch_array = netcap, generated_glitch_SYN, propagated_glitch_SYN
                           #criticality,glitch_array = read_criticality_metric_files.read_criticality_files(syn_criticality_file_path,out_criticality_file_path,N,in_out_list)   # Reads the criticality files to idntify critical gates TODO: fix 
                           #--------------------------------------------------#
   		                   #comparison[0] = arrivalmax-arrivalmin;
                           #comparison[1] = inertialdelay
                           #comparison[2] = glitch_count (from simulation)  
                           #critical_AM,Powerfrac,comparison[:,0:2] = postprocessAM(N,AMsol,glitch_array[1],F,Glog,gate_output_wire_capacitance,Cref,Opsize,gate_type_list,parasiticDelay,input_stage_data,leak_threshold) # atkr commented
                           # atkr added
                           glitchcount_AM = toggle_count_array_AM[:,2]# TODO: fix
                           #glitchcount_AM= 0
                           #activityFactor = toggle_count_array_AM[:,0]/sum(toggle_count_array_AM[:,0]) #TODO: fix
                           if(use_leakdata):
                              print("Info: main(): using provided leak data to find critical gates\n")
                              print(f"Info: main(): Enter 'yes' if appropriate {circuit_name}_leakscore.txt is copied at {path_final_AM}/{circuit_name}_leakscore")
                              print(f"Info: main(): VCD creation: /home/ee18s050/cadence/digital_design/synthesis_4/programs/atkr_genvcdsaif.py {circuit_name} {inputbits} 0 100 set1\nInfo: main(): Score calculation: /home/ee18s050/cadence/digital_design/synthesis_4/programs/atkr_computeleakscore.py {circuit_name} {inputbits} 0 100 set0") 
                              print(f"Info: main(): After ectering yes if leaskscore file in the given path is not found, {leakpath_AM} will be used.") 
                              leakpath = path_final_AM+"/"+circuit_name+"_leakscore/"+circuit_name+"_leakscore.txt"
                              #while (input("Your choice :").casefold() != 'yes'.casefold() ):
                              #  print()
                              if not os.path.exists(leakpath):
                                print(f"Warning: main(): {leakpath} is not found so using dummy file {leakpath_AM}")
                                leakpath = leakpath_AM
                              leakscore_AM =  get_leaks.get_leaks(circuit_files_directory,circuit_name,leakpath)
                           else:
                              print("Info: main(): using glitch count to find critical gates\n")
                              leakscore_AM =  toggle_count_array_AM[:,2]
                           if os.path.exists(leakpath_notiming):
                              leakscore_notiming = get_leaks.get_leaks(circuit_files_directory,circuit_name,leakpath_notiming)
                           else:
                              print(f"Error: main(): notiming score not found in {leakpath_notiming}")
                              sys.exit(0)
                           #gate_length = 196#TODO:fix
                           maxGlitch,minGlitch = analyse_critical(leakscore_notiming,leakscore_AM,glitchcount_AM,Iparr,gate_type_list,gate_name,noOfGatesToConstraint)
                           #critical_AM[:,1] is 1 when minimize_glitch
                           #critical_AM[:,0] is 1 when maximise_glitch
                           critical_AM,Powerfrac,comparison[:,0:2] = postprocessAM(N,AMsol,leakscore_AM,glitchcount_AM,F,Glog,gate_output_wire_capacitance,Cref,Opsize,gate_type_list,parasiticDelay,maxGlitch,minGlitch)  # atkr modified giving actial glitches for thresholding
                           print(f'Info: main(): Starting Glitch Optimisation GP')
                           isValid,GMsol,primary_gates_GM_sizes,modifiedGates,leakcriticalGates,glitchcriticalGates,leakcriticalGatewithPI = glitchOptObj(AMsol,N,T0,F,Opsize,Glog,Iparr,indIparr,Ips,maxIp,Powerfrac,AMsol["variables"]["a"], parasiticDelay,gate_output_wire_capacitance, Cref,level_of_gate_inputs_in,circuit_name,dont_consider_transition_time,comparison[:,1],critical_AM,excessP,glitchExponent,maxGsize,twall,inertial_delay_frac) # Sets up the
                           if not isValid:
                              print("\n#------------------- RESULT SUMMARY -----------------------#")
                              print(f'Error: summary: circuit_name {circuit_name}') 
                              print(f'Error: summary: Tfrac_set {twall}') 
                              print(f'Error: summary: Afrac_set {excessP}') 
                              print(f'Error: summary: Gates to constraint {noOfGatesToConstraint}') 
                              print(f'Error: summary: Twall {T0}') 
                              print(f'Error: summary: Awall {sum(AMsol["variables"]["x"])}') 
                              print(f'Error: summary: Total_gates {N}')
                              print(f'Error: summary: Error Occured')
                              print("#----------------------------------------------------------#")
                              #-------------------------------------------------------------------------------------------#
                              # logging into summary 
                              #-------------------------------------------------------------------------------------------#
                              summaryhandler = open(path_final+"/summary.txt",'w')
                              summaryhandler.write("\n#------------------- RESULT SUMMARY -----------------------#\n")
                              summaryhandler.write(f'Error: summary: circuit_name {circuit_name}\n') 
                              summaryhandler.write(f'Error: summary: Tfrac_set {twall}\n') 
                              summaryhandler.write(f'Error: summary: Afrac_set {excessP}\n') 
                              summaryhandler.write(f'Error: summary: Gates to constraint {noOfGatesToConstraint}\n') 
                              summaryhandler.write(f'Error: summary: Twall {T0}\n') 
                              summaryhandler.write(f'Error: summary: Awall {sum(AMsol["variables"]["x"])}\n') 
                              summaryhandler.write(f'Error: summary: Total_gates {N}\n')
                              summaryhandler.write(f'Error: summary: Error Occured\n')
                              summaryhandler.write("#----------------------------------------------------------#\n")
                              summaryhandler.close() 
                              continue
                           # GM problem using GPKit and the solver used is Mosek
                           if(GMsol != None):
                               GMsizes = GMsol["variables"]["x"]
                               GMarrival = GMsol["variables"]["a"]
                           primary_gates_details[:,2] = primary_gates_GM_sizes
                           comparison[:,16] = gate_type_list.reshape(len(gate_type_list))
                           comparison[:,17] = out_list
                           path_final_GM = os.path.join(path_final,'GM')
                           if not os.path.exists(path_final_GM):
                               os.makedirs(path_final_GM)
                               print("Info: main():",path_final_GM, "created")
                           else:
                               print("Info: main():", path_final_GM, "already exists")
                           np.savetxt(path_final_GM + "/GMsizes.txt",GMsizes)
                           GMsizes = round_off_function.round_off_fn(round_off_option,GMsizes)
                           run_mode = "GM"
                           verilog_destination_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','simulation_results',circuit_name,run_name,'GM', 'new_verilog_' + run_name + '.v')
                           library_destination_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','simulation_results',circuit_name,run_name,'GM', 'new_lib_' + run_name + '.lib')
                           source_verilog_write_file = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','simulation_results',circuit_name,run_name,'GM', 'new_verilog_source_' + run_name + '.v')
                           generate_library_and_netlist_files.generate_library_and_netlist_files(run_mode,path_final_GM,netlist_file,source_verilog_write_file,verilog_input_file,verilog_destination_file,library_input_file,library_destination_file)          # Generates the library files for the obtained GM sizes                 
                           #csv_format_local_array_GM = timing,area,glitch_power,total_power,notiming_transition,timing_tranition,glitches 
                           #toggle_count_array = [notiming toggle, timing toggle, glitch in each gate] 
                           #csv_format_local_array_GM,glitch_count_array_GM = run_simulation.run_simulation(circuit_name,run_number,auxillary_files_directory,circuit_files_directory,path_final_GM,csv_format_array) # Runs simulation using random input vectors using cadence NCSim and captures power consumptionnumber using Cadence Genus  # atkr commented
                           csv_format_local_array_GM,toggle_count_array_GM = run_simulation.run_simulation(circuit_name,run_number,auxillary_files_directory,circuit_files_directory,path_final_GM,csv_format_array) # Runs simulation using random input vectors using cadence NCSim and captures power consumption number using Cadence Genus  # atkr modified
                           #comparison[0] = arrivalmax-arrivalmin;
                           #comparison[1] = inertialdelay
                           #comparison[2] = glitch_count (from criticality)
                           # atkr modified for readability
                           glitchcount_GM = toggle_count_array_GM[:,2] 
                           #critical_GM,comparison[:,3:5] = postprocessGM(N,GMsol,glitchcount_AM,F,Glog,gate_output_wire_capacitance,Cref,Opsize,gate_type_list,parasiticDelay,input_stage_data,use_leakdata) # TODO: fix
                           csv_format_array[[4,9,11,13,21,23,25]] = csv_format_local_array_GM
                           #comparison[:,5] = glitch_count_array_GM # atkr commented
                           comparison[:,5] = toggle_count_array_GM[:,2] # atkr modified
                           comparison[:,6] = critical_AM[:,0]
                           comparison[:,7] = critical_AM[:,0] #TODO:Fix
   		                   #comparison[0] = arrivalmax-arrivalmin (AM);
                           #comparison[1] = inertialdelay (AM)
                           #comparison[2] = glitch_count (AM from Simulation)
   		                   #comparison[3] = arrivalmax-arrivalmin (GM);
                           #comparison[4] = inertialdelay (GM)
                           #comparison[5] = glitch_count (GM from Simulation)
                           #comparison[6] = criticalGates (AM)
                           #comparison[7] = criticalGates (GM)
                           # atkr added
                           totalIncreaseInGlitchCount = csv_format_local_array_GM[6] - csv_format_local_array_AM[6]
                           print(f'Info: main(): No of glitches in AM {csv_format_local_array_AM[6]} and in GM {csv_format_local_array_GM[6]}.Overall Increase in glitch count {totalIncreaseInGlitchCount}')
                           IncreaseInGlitchCountOnLeakCriticalGatewoPI = 0
                           IncreaseInGlitchCountOnGlitchCriticalGatewoPI = 0
                           IncreaseInGlitchCountOnLeakCriticalGatewPI = 0
                           IncreaseInGlitchCountOnGlitchCriticalGatewPI = 0
                           #print(f'Debug: main(): leakcriticalGates {leakcriticalGates}')
                           #print(f'Debug: main(): primarygates {primarygates}')
                           primary_gate_index =  [i for i, x in enumerate(primarygates) if x]
                           for gate in leakcriticalGates:
                              IncreaseInGlitch = comparison[gate,5]-comparison[gate,2]
                              if(gate in primary_gate_index):
                                  #print(f'Debug: main(): WITHPI: Increase in glitch on {gate_name[gate]} is {IncreseInGlitchOnGate} size from {AMsol["variables"]["x"][gate]} to {GMsol["variables"]["x"][gate]}')
                                  IncreaseInGlitchCountOnLeakCriticalGatewPI += IncreaseInGlitch
                              else: 
                                  #print(f'Debug: main(): WITHNOPI: Increase in glitch on {gate_name[gate]} is {IncreseInGlitchOnGate} size from {AMsol["variables"]["x"][gate]} to {GMsol["variables"]["x"][gate]}')
                                  IncreaseInGlitchCountOnLeakCriticalGatewoPI += IncreaseInGlitch
                           for gate in glitchcriticalGates:
                              IncreaseInGlitch = comparison[gate,5]-comparison[gate,2]
                              if(gate in primary_gate_index):
                                  #print(f'Debug: main(): WITHPI: Increase in glitch on {gate_name[gate]} is {IncreseInGlitchOnGate} size from {AMsol["variables"]["x"][gate]} to {GMsol["variables"]["x"][gate]}')
                                  IncreaseInGlitchCountOnGlitchCriticalGatewPI += IncreaseInGlitch
                              else: 
                                  #print(f'Debug: main(): WITHNOPI: Increase in glitch on {gate_name[gate]} is {IncreseInGlitchOnGate} size from {AMsol["variables"]["x"][gate]} to {GMsol["variables"]["x"][gate]}')
                                  IncreaseInGlitchCountOnGlitchCriticalGatewoPI += IncreaseInGlitch
                           IncreaseInGlitchCountOnLeakCriticalGate = IncreaseInGlitchCountOnLeakCriticalGatewPI +  IncreaseInGlitchCountOnLeakCriticalGatewoPI
                           IncreaseInGlitchCountOnGlitchCriticalGate = IncreaseInGlitchCountOnGlitchCriticalGatewPI +  IncreaseInGlitchCountOnGlitchCriticalGatewoPI
                           #print(f'Info: main(): Avg Increase in glitch on leak critical gates are {IncreaseInGlitchCountOnLeakCriticalGate/len(leakcriticalGates)}')
                           #print(f'Info: main(): Avg Increase in glitch on glitch critical gates are {IncreaseInGlitchCountOnGlitchCriticalGate/len(glitchcriticalGates)}')
                           print(f'Info: main(): Total increase in glitch are {totalIncreaseInGlitchCount} while contributed by leak CriticalGates are {IncreaseInGlitchCountOnLeakCriticalGate} which is {(IncreaseInGlitchCountOnLeakCriticalGate/totalIncreaseInGlitchCount)*100}%\n')
                           metahandler = open(path_final+"/metadata.csv",'w')
                           metahandler.write("gate_name,gate_type,gate_number,level,,AMgate_sizes,Gmgate_sizes,gate_arrival_time,notiming_leakscore,AM_leakscore,to_minimize,to_maximize,is_PI,is_modified,AM_glitch_count,GM_glitch_count,delta_glitch_count\n")
                           ismodifiedGates = [1 if i in modifiedGates else 0 for i in range(N)]
                           levelofgate = [max(levellist) for levellist in level_of_gate_inputs_in]
                           indices = 0
                           for name,gate_type,amsize,gmsize,arrival,leak_notiming,leak_AM,isleakcritical,isglitchcritical,ispi,is_modified,level,AM_glitch,GM_glitch in zip(gate_name,gate_type_list,AMsizes,GMsizes,GMarrival,leakscore_notiming,leakscore_AM, critical_AM[:,1],critical_AM[:,0],primarygates,ismodifiedGates,levelofgate,glitchcount_AM,glitchcount_GM):
                               #field = name+","+gate_type[0]+","+str(leak_notiming)+","+str(leak_AM)+","
                               field = name+","+gate_type[0]+","+str(indices)+","+str(level)+","
                               field += str(round(amsize,4))+","+str(round(gmsize,4))+","+str(round(arrival,4))+","+str(leak_notiming)+","+str(leak_AM)+","
                               field += "yes," if(isleakcritical) else "No,"
                               field += "yes," if(isglitchcritical) else "No,"
                               field += "yes," if(ispi) else "No,"
                               field += "yes," if(is_modified) else "No,"
                               field += str(AM_glitch)+","+str(GM_glitch)+","+str(GM_glitch-AM_glitch)+"\n"
                               metahandler.write(field)
                               indices = indices+1
                           metahandler.close()
                           print("#------------------- RESULT SUMMARY -----------------------#")
                           print(f'Info: summary: {notes_to_print}') 
                           print(f'Info: summary: circuit_name {circuit_name}') 
                           print(f'Info: summary: Tfrac_set {twall}') 
                           print(f'Info: summary: Afrac_set {excessP}') 
                           print(f'Info: summary: Twall {T0}') 
                           print(f'Info: summary: Awall {sum(AMsol["variables"]["x"])}')
                           print(f'Info: summary: using external thresholding {use_leakdata}')
                           print(f'Info: summary: gates to constraint is {noOfGatesToConstraint}') 
                           print(f'Info: summary: Min_Glitch_gates {len(leakcriticalGates)}')
                           print(f'Info: summary: Min_Glitch_with_PI {len(leakcriticalGatewithPI)}')
                           print(f'Info: summary: Max_Glitch_gates {len(glitchcriticalGates)}')
                           print(f'Info: summary: Modified_gates {len(modifiedGates)}')
                           print(f'Info: summary: Total_gates {N}')
                           print(f'Info: summary: Tfrac_achieved {GMsol["variables"]["Ts"]/T0}') 
                           print(f'Info: summary: Afrac_achieved {sum(GMsol["variables"]["x"])/sum(AMsol["variables"]["x"])}') 
                           print(f'Info: summary: Total_glitch {totalIncreaseInGlitchCount}') 
                           print(f'Info: summary: Total_MIN_critical_glitch {IncreaseInGlitchCountOnLeakCriticalGate}')
                           print(f'Info: summary: wPI_min_Critical_glitch {IncreaseInGlitchCountOnLeakCriticalGatewPI}')
                           print(f'Info: summary: woPI_min_critical_glitch {IncreaseInGlitchCountOnLeakCriticalGatewoPI}')
                           print(f'Info: summary: Total_MAX_Critical_glitch {IncreaseInGlitchCountOnGlitchCriticalGate}')
                           print(f'Info: summary: wPI_max_critical_glitch {IncreaseInGlitchCountOnGlitchCriticalGatewPI}')
                           print(f'Info: summary: woPI_max_critical_glitch {IncreaseInGlitchCountOnGlitchCriticalGatewoPI}')
                           print("#----------------------------------------------------------#")
                           #-------------------------------------------------------------------------------------------#
                           # logging into summary 
                           #-------------------------------------------------------------------------------------------#
                           summaryhandler = open(path_final+"/summary.txt",'w')
                           summaryhandler.write("#------------------- RESULT SUMMARY -----------------------#\n")
                           summaryhandler.write(f'Info: summary: {notes_to_print}\n') 
                           summaryhandler.write(f'Info: summary: circuit_name {circuit_name}\n') 
                           summaryhandler.write(f'Info: summary: Tfrac_set {twall}\n') 
                           summaryhandler.write(f'Info: summary: Afrac_set {excessP}\n') 
                           summaryhandler.write(f'Info: summary: Twall {T0}\n') 
                           summaryhandler.write(f'Info: summary: Awall {sum(AMsol["variables"]["x"])}\n') 
                           summaryhandler.write(f'Info: summary: using external thresholding {use_leakdata}\n')
                           summaryhandler.write(f'Info: summary: gates to constraint is {noOfGatesToConstraint}\n') 
                           summaryhandler.write(f'Info: summary: Min_Glitch_gates {len(leakcriticalGates)}\n')
                           summaryhandler.write(f'Info: summary: Min_Glitch_with_PI {len(leakcriticalGatewithPI)}\n')
                           summaryhandler.write(f'Info: summary: Max_Glitch_gates {len(glitchcriticalGates)}\n')
                           summaryhandler.write(f'Info: summary: Modified_gates {len(modifiedGates)}\n')
                           summaryhandler.write(f'Info: summary: Total_gates {N}\n')
                           summaryhandler.write(f'Info: summary: Tfrac_achieved {GMsol["variables"]["Ts"]/T0}\n') 
                           summaryhandler.write(f'Info: summary: Afrac_achieved {sum(GMsol["variables"]["x"])/sum(AMsol["variables"]["x"])}\n') 
                           summaryhandler.write(f'Info: summary: Total_glitch {totalIncreaseInGlitchCount}\n') 
                           summaryhandler.write(f'Info: summary: Total_MIN_critical_glitch {IncreaseInGlitchCountOnLeakCriticalGate}\n')
                           summaryhandler.write(f'Info: summary: wPI_min_Critical_glitch {IncreaseInGlitchCountOnLeakCriticalGatewPI}\n')
                           summaryhandler.write(f'Info: summary: woPI_min_critical_glitch {IncreaseInGlitchCountOnLeakCriticalGatewoPI}\n')
                           summaryhandler.write(f'Info: summary: Total_MAX_Critical_glitch  {IncreaseInGlitchCountOnGlitchCriticalGate}\n')
                           summaryhandler.write(f'Info: summary: wPI_max_critical_glitch  {IncreaseInGlitchCountOnGlitchCriticalGatewPI}\n')
                           summaryhandler.write(f'Info: summary: woPI_max_critical_glitch  {IncreaseInGlitchCountOnGlitchCriticalGatewoPI}\n')
                           summaryhandler.write("#----------------------------------------------------------#\n")
                           summaryhandler.close()
                           # atkr modified finding temporary leak score
                           vcd_testbench_file = f"{circuit_files_directory}/{circuit_name}/{circuit_name}_vcd_tb.v"
                           sdf_cmd_file = f"{path_final_GM}/{circuit_name}_results/{circuit_name}.sdf.X"
                           leakscore_dir = f"{path_final_GM}/{circuit_name}_leakscore/" 
                           os.makedirs(leakscore_dir,exist_ok=True)
                           shutil.copy2(vcd_testbench_file,leakscore_dir)
                           shutil.copy2(sdf_cmd_file,leakscore_dir)
                           #findleakscore(circuit_name,path_final,circuit_files_directory,"AM",0,2000,100)
                           print("Info: main(): generate leakscore for GlichOpt netlist")
                           print(f"Info: main(): Enter 'yes' if appropriate {circuit_name}_leakscore.txt is generated at {path_final_GM}/{circuit_name}_leakscore")
                           print(f"Info: main(): VCD creation: /home/ee18s050/cadence/digital_design/synthesis_4/programs/atkr_genvcdsaif.py {circuit_name} {inputbits} 0 100 set1\nInfo: main(): Score calculation: /home/ee18s050/cadence/digital_design/synthesis_4/programs/atkr_computeleakscore.py {circuit_name} {inputbits} 0 100 set0") 
                           print(f"Info: main(): After ectering yes if leaskscore file in the given path is not found, {leakpath_AM} will be used.") 
                           while (input("Your choice :").casefold() != 'yes'.casefold() ):
                            print()
                           leakpath = path_final_GM+"/"+circuit_name+"_leakscore/"+circuit_name+"_leakscore.txt"
                           if not os.path.exists(leakpath):
                            print(f"Warning: main(): {leakpath} is not found so using dummy file {leakpath_AM} to update the csv file")
                            leakpath = leakpath_AM
                           updateLeakCsv(leakpath,path_final+"/metadata.csv",circuit_name)
                           print(f"\nInfo: main(): For more metadata check libreoffice --calc {path_final}/metadata_updated.csv\n")
                           # /home/ee18s050/cadence/digital_design/synthesis_4/programs_GOptAnalysis/compare_update_leak.py GM/SBOX_leakscore/SBOX_leakscore.txt


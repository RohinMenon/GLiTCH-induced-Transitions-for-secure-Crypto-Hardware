
#####VER2:
#identifies and,or,buffer as nand+ inverter,nor+ inverter,inverter + inverter respectively

#if gate 1 is connected to gate 17, the F matrix would contain the logical effort of gate 17 in
#the position (1,17) and not the logical effort of gate 1 which is the case in the verilog_parser_ver1

###VER3:
#Identifies all gates with all primary inputs in the inital pass irrespective of the fan_in of the gate

###VER4:
#Identifies XOR gates and assigns appropriate logical effort to its inputs according to how an xor gate is built using cmos logic 

##VER5:
#Added Shivani's criticality metric for gates. Gates' criticality metric contained in a array called 'criticality'

##VER6:
#Added reading generated and propagated glitches from csv file generated using shivani's scripts

##VER6:
#Changed logical effort of NAND2, NAND3, NAND4, NOR2, NOR3, NOR4 using values from library file

##VER7:
#Changed logical effort using capacitance ratios from library file

#VER8:
#Used logical effort obtained from simulations and also included parasitic delay values from simulations for a few gates

#VER9
#Modelled XOR XNOR same as NANDs and NORs

from pylab import *
import numpy as np
import time
import sys
from os import path
from scipy.interpolate import interp1d as inp


start_time = time.time()
np.set_printoptions(threshold=sys.maxsize)

##verilog_file_path = "D:/library file/ordered/c2670_genus_2_modified_topological_order.txt"
##criticality_metric_csv_file = "D:/python programs/temp/c2670_SynCriticality_2.txt"
##glitch_details_csv_file = "D:/python programs/temp/c2670_out_2.txt"

##D://library file/
def parser(circuit_files_path, circuit_name):
    verilog_file_path = path.join(circuit_files_path,circuit_name,circuit_name + "_genus.txt")
    
    logical_effort_map = {"NOT1" : 1,"NOT" : 1,"NAND2" : 1.25,"NAND3" : 1.53,"NAND4" : 1.76,"NOR2" : 1.8,"NOR3" : 2.38,"NOR4" : 3.24, "XOR2" : 3.19 ,"XNOR2":3.00}
    parasitic_delay_map = {"NOT" : 2.1,"NOT1" : 2.1,"NAND2" : 3.45,"NAND3" : 5.3,"NAND4" : 7.34,"NOR2" : 3.92,"NOR3" : 6.82,"NOR4" : 9.89, "XOR2" : 10.48 ,"XNOR2" : 10.47}

    inputs = []
    outputs = []
    logical_effort = {}
    parasitic_delay = {}
    current_gates = []
    to_be_checked = []
    gate_name = []
    in_out_list = []
    in_length = []
    temp = []
    temp1 = []
    current_gates_temp = []
    outputs_so_far = []
    and_or_buffer_gates = []
    xorxnor_gates = []
    gate_number_map = {}
    buffer_gates = []
    check = []
    xorxnor_gates_dict = {}
    xorxnor_gates_input_list = []
    fan_in_list = {}
    node_level = {}
    level_of_gate_inputs = []
    primary_gates = []
    
    try:
        file = open(verilog_file_path, "r")
        contents = file.readlines()

        # Get input list
        for i in range(0, len(contents)):
            if "input" in contents[i] and "//" not in contents[i]:
                input_start = i
                break
        for i in range(input_start, len(contents)):
        	if "input" in contents[i] and "//" not in contents[i]:
        		input_end = i 
        # Get input list - updated to handle comma-separated vector and scalar inputs
        for i in range(input_start, input_end + 1):
        	line = contents[i].strip().strip('\n').strip(';')
        	if 'input' in line:
        		line = line.replace('input', '').strip()
        	# Split the line by commas to handle each signal separately
        	signals = line.split(',')
        	for signal in signals:
        		signal = signal.strip()
        		# Handle vector inputs like [63:0] idat
        		if '[' in signal:
        			vector_parts = signal.split(']')
        			range_part = vector_parts[0].strip('[').split(':')
        			signal_name = vector_parts[1].strip()
        			high = int(range_part[0])
        			low = int(range_part[1])
        			for bit in range(low, high + 1):
        				inputs.append(f"{signal_name}[{bit}]")
        	else:
        		# Handle scalar inputs
        		if signal:
        			inputs.append(signal)

        for i in range(len(inputs)):
            inputs[i] = inputs[i].strip()
            node_level[inputs[i]] = 0
        # Get output list - similar modification for outputs
        for i in range(0, len(contents)):
            if "output" in contents[i] and "//" not in contents[i]:
                output_start = i
                break
        #print(inputs)
        for i in range(output_start, len(contents)):
            if ";" in contents[i]:
                output_end = i
                break

        for i in range(output_start, output_end+1):
            line = contents[i].strip().strip('\n').strip(';').strip(',')
            if 'output' in line:
                line = line.replace('output', '').strip()
            
            # Handle vector outputs like [3:0] out
            if '[' in line:
                vector_parts = line.split(']')
                range_part = vector_parts[0].strip('[').split(':')
                signal_name = vector_parts[1].strip()
                high = int(range_part[0])
                low = int(range_part[1])
                for bit in range(low, high+1):
                    outputs.append(f"{signal_name}[{bit}]")
            else:
                # Handle scalar outputs
                signals = line.split(',')
                for signal in signals:
                    if signal.strip():
                        outputs.append(signal.strip())

        for i in range(len(outputs)):
            outputs[i] = outputs[i].strip()

        outputs_so_far = list(inputs)

        #print(outputs)
#        print("new_one")
#        print("testing")

        ##for i in range(0,len(contents)):
        ##    if "wire" in contents[i] and "//" not in contents[i]:
        ##        wire_start=i
        ##        break
        ##for i in range(wire_start,len(contents)):
        ##    if ";" in contents[i]:
        ##        wire_end = i;
        ##        break

        for i in range(len(contents)):            
            if "wire" in contents[i]:
                wire_end = i
            if "endmodule" in contents[i]:
                gate_end = i - 1

        while ';' not in contents[wire_end]:
            wire_end = wire_end + 1

        gate_start = wire_end + 1

        while contents[gate_start] == '\n':
            gate_start = gate_start + 1

        while contents[gate_end] == '\n':
            gate_end = gate_end - 1

        and_or_gate_count = 0
        xorxnor_count = 0
        
        for i in range(gate_start,gate_end+1):
            gate_type = contents[i].split()[0]
            gate_type = gate_type.upper()
            if(gate_type == "AND" or gate_type =="OR" or gate_type =="BUFF"):
                and_or_gate_count = and_or_gate_count + 1
            if(gate_type == "XORX" or gate_type =="XNORX"):
                xorxnor_count = xorxnor_count + 1

        #N = gate_end - gate_start + 1 + and_or_gate_count + xorxnor_count * 2               
        N = gate_end - gate_start + 1 + and_or_gate_count                 

        ##gate_start = wire_end+2
        ##gate_end   = len(contents)-3



        to_be_checked=list(range(gate_start,gate_end+1))
        gate_type_list = np.zeros(shape = (N,1),dtype=object)

        #Create logical effort dictionary for all gates
        num = 0
        for i in range(gate_start,gate_end+1):
            gate_name.append(contents[i].split()[1])
            gate_type = contents[i].split()[0]
            gate_type = gate_type.upper()                   
            fan_in = len(contents[i].rstrip(';\n').split('(')[1].rstrip(')').split(',')[1:])
            if gate_type == "BUF":
                gate_type = "BUFF"
            gate_type = gate_type + str(fan_in)
            gate_type_list[num,0] = gate_type
            #if(num == 0):
            #    print("gate_type = ",gate_type)
        #    gate_type = (contents[i].split()[1]).split('_')[0]
        #    fan_in = len(contents[i].rstrip(';\n').split('(')[1].rstrip(')').split(',')[1:])
            
            if("XORX" not in gate_type or "XNORX" not in gate_type ):
                gate_number_map[i] = num
                logical_effort[gate_number_map[i]]=logical_effort_map[gate_type]
                parasitic_delay[gate_number_map[i]]=parasitic_delay_map[gate_type]
        #        fan_in_list[num] = fan_in
            else:
                xorxnor_gates.append(i)
                gate_number_map[i] = num + 2
                num = num + 2
                logical_effort[gate_number_map[i]-2]= 1.0
                logical_effort[gate_number_map[i]-1]= 1.0
                logical_effort[gate_number_map[i]]= logical_effort_map[gate_type]
                parasitic_delay[gate_number_map[i]]=parasitic_delay_map[gate_type]
        #        fan_in_list[num] = fan_in
                fan_in_list[num-2] = 1
                fan_in_list[num-1] = 1

            fan_in_list[num] = fan_in
            gate_type = gate_type[:-1]
            if(gate_type == "AND" or gate_type =="OR" or gate_type =="BUFF"):
                and_or_buffer_gates.append(i)
                num = num + 1
                logical_effort[gate_number_map[i]+1]= logical_effort_map["NOT1"]
                parasitic_delay[gate_number_map[i] + 1]= parasitic_delay_map["NOT1"]
                fan_in_list[num] = 1
        ##    else:
        ##        if(gate_type == "XOR"):
        ##            xorxnor_gates.append(i)
        ##            num = num + 2
        ##            logical_effort[gate_number_map[i]]= 1
        ##            logical_effort[gate_number_map[i]+1]= 1
            num = num + 1
                
        for count,i in enumerate(xorxnor_gates):
            xorxnor_gates_dict[i] = count

        for i in xorxnor_gates:
            xorxnor_gates_input_list.append(list(range(1,3)))
            

#        N = gate_end - gate_start + 1 + len(and_or_buffer_gates) + len(xorxnor_gates) * 2 

        F = np.zeros((N,N))
        #######################################################################
        ##for i in range(gate_start,gate_end+1):
        ##    gate_type = (contents[i].split()[1]).split('_')[0]
        ##    gate_type = gate_type[:-1]
        ##    if(gate_type == "BUFF"):
        ##        buffer_gates.append(i)
        #######################################################################
        flag = 1
        gate_level_dict = {}     
        #Get the F matrix
        for i in range(gate_start,gate_end+1):
            gate_number = i-gate_start
            temp = contents[i].rstrip(';\n').split('(')[1].rstrip(')').split(',')
            temp.reverse()
            while(temp):
                temp1.append(temp.pop().strip())
            in_out_list.append(temp1)
            temp1 = []
            in_length.append(len(in_out_list[gate_number])-1)
            for j in in_out_list[gate_number][1:]:
                if j not in inputs:
                    flag = 0
                    break
            if(flag):
                current_gates.append(i)
                to_be_checked.remove(i)
                outputs_so_far.append(in_out_list[gate_number][0].strip())
                node_level[in_out_list[gate_number][0].strip()] = 1
                gate_level_dict[in_out_list[gate_number][0].strip()] = 1
               
            flag = 1


        for i in current_gates:
            if i in xorxnor_gates:
                F[gate_number_map[i] - xorxnor_gates_input_list[xorxnor_gates_dict[i]].pop()][gate_number_map[i]] = 2.0
                F[gate_number_map[i] - xorxnor_gates_input_list[xorxnor_gates_dict[i]].pop()][gate_number_map[i]] = 2.0
      
        level_count = 2
        out_list = [item[0] for item in in_out_list]

        while to_be_checked:  

            for i in current_gates:
                for j in to_be_checked:
                    gate_number_i = i - gate_start
                    gate_number_j = j - gate_start
                    if in_out_list[gate_number_i][0].strip() in in_out_list[gate_number_j][1:]:
                        if j in xorxnor_gates:
                            xorxnor_gate_index = xorxnor_gates_input_list[xorxnor_gates_dict[j]].pop()
                            if i in and_or_buffer_gates:
                                F[gate_number_map[i]][gate_number_map[i]+1] = 1
                                F[gate_number_map[i]+1][gate_number_map[j]-xorxnor_gate_index] = 1
                                F[gate_number_map[j]-xorxnor_gate_index][gate_number_map[j]] = logical_effort[gate_number_map[j]]
                                F[gate_number_map[i]+1][gate_number_map[j]] = logical_effort[gate_number_map[j]]
                            else:
                                F[gate_number_map[i]][gate_number_map[j]-xorxnor_gate_index] = 1
                                F[gate_number_map[j]-xorxnor_gate_index][gate_number_map[j]] = logical_effort[gate_number_map[j]]
                                F[gate_number_map[i]][gate_number_map[j]] = logical_effort[gate_number_map[j]]
                            for k in in_out_list[gate_number_j][1:]:
                                if k not in outputs_so_far:
                                    flag = 0
                                    break
                        else:
                            if i in and_or_buffer_gates:
                                F[gate_number_map[i]][gate_number_map[i]+1] = 1
                                F[gate_number_map[i]+1][gate_number_map[j]] = logical_effort[gate_number_map[j]]
                            else:
                                F[gate_number_map[i]][gate_number_map[j]] = logical_effort[gate_number_map[i]]

                        for k in in_out_list[gate_number_j][1:]:
                            if k not in outputs_so_far:
                                flag = 0
                                break
                        if flag:
                            if j not in current_gates_temp:
                                current_gates_temp.append(j)

                    flag = 1

            # 🔸 Even if nothing is added to current_gates_temp, go ahead and increment level
            if current_gates_temp:
                for u in current_gates_temp:
                    if u in to_be_checked:
                        to_be_checked.remove(u)
                        outputs_so_far.append(in_out_list[u - gate_start][0])
                        node_level[in_out_list[u - gate_start][0].strip()] = level_count
                        gate_level_dict[in_out_list[u - gate_start][0].strip()] = level_count

            # 🔸 Still increment level even if current_gates_temp was empty
            current_gates = list(current_gates_temp)
            current_gates_temp = []
            level_count += 1
        #print(gate_start)
        #print(gate_end)
        for i in range(gate_start,gate_end+1):
            gate_number_i = i-gate_start
            if(in_out_list[gate_number_i][0].strip() in outputs):
                gate_type = (contents[i].split()[1]).split('_')[0]
                gate_type = gate_type[:-1]
                if(gate_type =="BUFF" or gate_type=="OR" or gate_type=="AND"):
                   F[gate_number_map[i]][gate_number_map[i]+1] = 1
                   
        xorxnor_gates_input_list=[]
        print(gate_level_dict)
        for i in xorxnor_gates:
            xorxnor_gates_input_list.append(list(range(1,3)))
		
        #Create the logical effort matrix 
        Gate_logical_effort = np.zeros(N)

        for i in range(gate_start,gate_end+1):
            if i in and_or_buffer_gates:
                Gate_logical_effort[gate_number_map[i]] = logical_effort[gate_number_map[i]]
                Gate_logical_effort[gate_number_map[i]+1] = 1
            else:
                if i in xorxnor_gates:
                    Gate_logical_effort[gate_number_map[i]] = logical_effort[gate_number_map[i]]
                    while(xorxnor_gates_input_list[xorxnor_gates_dict[i]]):
                        Gate_logical_effort[gate_number_map[i]-xorxnor_gates_input_list[xorxnor_gates_dict[i]].pop()] = 1
                else:
                    Gate_logical_effort[gate_number_map[i]] = logical_effort[gate_number_map[i]]

        #Create the Output capacitance matrix
        Opsize = np.zeros(N)           

        for i in range(gate_start,gate_end+1):
            gate_number_i = i-gate_start
            if(in_out_list[gate_number_i][0].strip() in outputs):
                if i in and_or_buffer_gates:
                    Opsize[gate_number_map[i]+1] = 20
                else:    
                    Opsize[gate_number_map[i]] = 20
        fanout = np.sum(F!=0, axis=1)
        fanout_list = np.array([0,1,2,3,4,5,10,16,50,90])
        wire_length_list = np.array([0,6.5,13.8,22,35.4,54.6,88,180,284.3,500.4])
        wire_length = inp(fanout_list,wire_length_list,fill_value='extrapolate')
        gate_output_wire_capacitance = wire_length(fanout) * 0.0001382 * 1000
        #print(f'Info: parser(): wire_length is {wire_length}')
        for i in range(gate_start,gate_end + 1):
            gate_number = i - gate_start
            
            level_of_gate_inputs.append([node_level[y] for y in in_out_list[gate_number][1:]])

        #Create the primary gates thing:
        arrind = np.where(F!=0)         #Indices with non-zero 
                                    #Arrival time matrix (which are I/ps to gates)
        Iparr = array([arrind[0][np.where(arrind[1] == i)] for i in range(0,N)])
        for i in range(N):
            if(len(Iparr[i]) == 0):
                primary_gates.append(i)
        primary_gates_type_list = gate_type_list[primary_gates]
        no_of_primary_gates = len(primary_gates_type_list)
        
    except IOError:
        print("Verilog file not found")


    return F , Opsize , Gate_logical_effort , fan_in_list , parasitic_delay , gate_output_wire_capacitance, level_of_gate_inputs, primary_gates_type_list, no_of_primary_gates, gate_type_list,out_list,in_out_list,gate_name




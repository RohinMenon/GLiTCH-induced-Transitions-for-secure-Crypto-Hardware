#!/usr/bin/python3
import re
from pylab import *
import os



def get_gateorder(netlist_file):
        print(f'Info: vcd_toggle(): Extracting gate name')
                
        gate_node_dict = {}
        inputs=[]

        with open(netlist_file,"r") as f:
                contents=f.readlines()

                for i in range(0,len(contents)):
                        if "wire" in contents[i] and "//" not in contents[i]:
                                wire_start=i
                        if "endmodule" in contents[i]:
                                gate_end = i - 1
                for i in range(wire_start,len(contents)):
                        if ";" in contents[i]:
                                wire_end = i
                                break
                
                gate_start = wire_end + 1

                while contents[gate_start] == '\n':
                        gate_start = gate_start + 1

                while contents[gate_end] == '\n':
                        gate_end = gate_end - 1

                for i in range(0,len(contents)):
                        if "input" in contents[i] and "//" not in contents[i]:
                                input_start=i
                                break        
                for i in range(input_start,len(contents)):
                        if ";" in contents[i]:
                                input_end=i
                                break

                for i in range(input_start,input_end+1):
                    for j in range(0,len(contents[i].strip().strip('\n').split(','))):
                        inputs.append((contents[i].strip().strip('\n')).split(',')[j])
                    if(contents[i].strip().strip('\n')[-1] == ','):
                        inputs.pop()

                if(';' in inputs[-1]):
                    inputs[-1] = inputs[-1].replace(";","")     

                inputs[0]=inputs[0].replace("input","")

                for i in range(len(inputs)):
                        inputs[i] = inputs[i].strip()

                for i in range(gate_start,gate_end + 1):
                        node = contents[i].rstrip(';\n').split('(')[1].rstrip(')').split(',')[0]
                        node = node.strip()    
                        gate_node_dict[node] = i - gate_start

                for i in range(len(inputs)):
                        gate_node_dict[inputs[i]] = gate_end+i+1-gate_start

        f.close()
        return gate_node_dict # atkr modified


    

def get_transcount(gate_node_dict,saif_file):
        print(f'Info: vcd_toggle(): Calculating transitions')
        with open(saif_file,"r") as f1:
                contents_1 = f1.readlines()
                toggle_count_array = np.zeros(shape=(len(gate_node_dict)),dtype=int)
                i=0
                while "INSTANCE dut" not in contents_1[i]:
                        i = i + 1
                starting_net = i + 2
                i = starting_net
                while ')' not in contents_1[i]:
                        node_name = contents_1[i].rstrip('\n').strip().strip('(')
                        if ('\[' in node_name or '\]' in node_name):
                                node_name = '\\' + node_name
                                node_name = re.sub(r'\\\[',r'[',node_name)
                                node_name = re.sub(r'\\\]',r']',node_name)
                        toggle_count = int(re.search('\(TC (.+?)\)', contents_1[i+2]).group(1))
                        toggle_count_array[gate_node_dict[node_name]] = toggle_count
                        i = i + 4
        f1.close()
        return toggle_count_array 

#gate_dict = get_gateorder("/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/SBOX/SBOX_genus.txt")
#tc = get_transcount(gate_dict,"/home/ee18s050/cadence/digital_design/synthesis_4/arvindtkr/vcdGenaration/100_65529.saif")
#for node in gate_dict.keys():
#    print(f"HD({node}) : {tc[gate_dict[node]]}",end =', ')

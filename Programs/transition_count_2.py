import re
from pylab import *
import os

# netlist_file: /home/ee18s050/cadence/digital_design/synthesis_4/circuit_files/c432/c432_genus.txt
# circuit_name: c142
# path_final : /home/ee18s050/cadence/digital_design/synthesis_4/simulation_results/c432/c432_36/AM


def transition_count(circuit_name,netlist_file,path_final):
        print(f'Info: transition_count(): Calculating glitches')
                
        gate_node_dict = {}
        inputs=[]


        with_delay_saif_file = os.path.join(path_final,f'{circuit_name}_results',f'{circuit_name}_sdf_vcd2saif.saif')

        without_delay_saif_file = os.path.join(path_final,f'{circuit_name}_results',f'{circuit_name}_vcd2saif.saif')

        with open(netlist_file,"r") as f, open(with_delay_saif_file,"r") as f1, open(without_delay_saif_file,"r") as f2:
                contents=f.readlines()
                contents_1 = f1.readlines()
                contents_2 = f2.readlines()

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

                toggle_count_array = np.zeros(shape=(gate_end - gate_start + 1, 3),dtype=int)
                
                for i in range(gate_start,gate_end + 1):
                        node = contents[i].rstrip(';\n').split('(')[1].rstrip(')').split(',')[0]
                        node = node.strip()     
                        gate_node_dict[node] = i - gate_start

                i=0

                while "NET" not in contents_1[i]:
                        i = i + 1

                starting_net = i + 1

                i = starting_net

                while ')' not in contents_1[i]:
                        node_name = contents_1[i].rstrip('\n').strip().strip('(')
                       	print(node_name)
                        if '\\[' in node_name or '\\]' in node_name:
                            node_name = node_name.replace('\\[', '[')
                            node_name = node_name.replace('\\]', ']')
                        
                        if node_name.startswith('A_init') or node_name=="reset" or node_name =="clk" or node_name.startswith('share_in') or node_name=="N" or node_name.startswith('buffer[') or node_name.startswith('in[') or node_name.startswith('file') or node_name.startswith('x[') or node_name.startswith('k[') or node_name.startswith('random_number') or node_name.startswith('res') or node_name.startswith('key') or node_name=="load" or node_name == "CLK":    
                          i += 4
                          continue
                        #print(node_name)
                        if node_name not in inputs:

                                toggle_count = int(re.search('\(TC (.+?)\)', contents_1[i+2]).group(1))
                                        
                                toggle_count_array[gate_node_dict[node_name],0] = toggle_count


                                 
                        i = i + 4

                i = 0
                
                while "NET" not in contents_2[i] :
                        i = i + 1

                starting_net = i + 1

                i = starting_net

                while ')' not in contents_2[i] :
                        node_name = contents_2[i].rstrip('\n').strip().strip('(')
                        if '\\[' in node_name or '\\]' in node_name:
                            node_name = node_name.replace('\\[', '[')
                            node_name = node_name.replace('\\]', ']')
                        
                        if node_name.startswith('A_init') or node_name=="reset" or node_name.startswith('share_in') or node_name =="clk" or node_name=="N" or node_name.startswith('buffer[') or node_name.startswith('in[') or node_name.startswith('x[') or node_name.startswith('file') or node_name.startswith('random_number') or node_name.startswith('k[') or node_name.startswith('key') or node_name.startswith('res') or node_name=="load" or node_name == "CLK":    
                          i += 4
                          continue
                        if node_name not in inputs:

                                toggle_count = int(re.search('\(TC (.+?)\)', contents_2[i+2]).group(1))

                                toggle_count_array[gate_node_dict[node_name],1] = toggle_count



                                 

                        i = i + 4

                toggle_count_array[:,2] = toggle_count_array[:,0] - toggle_count_array[:,1]

                Total_Transitions = np.sum(toggle_count_array[:,0])
                Functional_Transitions = np.sum(toggle_count_array[:,1])
                No_of_glitches = np.sum(toggle_count_array[:,2])


        f.close()
        f1.close()
        f2.close()

        #return Total_Transitions,Functional_Transitions,No_of_glitches,toggle_count_array[:,2] # atkr commented 
        return Total_Transitions,Functional_Transitions,No_of_glitches,toggle_count_array # atkr modified




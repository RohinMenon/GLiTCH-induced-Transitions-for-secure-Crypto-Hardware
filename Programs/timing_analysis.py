import numpy as np
import re
from operator import itemgetter
import sys

np.set_printoptions(threshold=sys.maxsize)
netlist_file_path = "c6288_netlist.v"
sdf_file_path = "c6288.sdf"

def timing_analysis(netlist_file_path,sdf_file_path):
    
    list_of_in_outs = []
    in_outs = []
    in_outs_of_this_gate = []
    instance_name = []
    inputs = []
    outputs = []
    output_node_map = {}
    instance_map = {}

    current_gates=[]
    to_be_checked=[]
    outputs_so_far=[]
    current_gates_temp = []


    ##try:
    ##    file=open(sdf_file_path,"r")
    ##    contents=file.readlines()
    ##
    ##    
        

    try:
        file=open(netlist_file_path,"r")
        contents=file.readlines()

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

        #Get output list
        for i in range(0,len(contents)):
            if "output" in contents[i] and "//" not in contents[i]:
                output_start=i
                break        
        for i in range(output_start,len(contents)):
            if ";" in contents[i]:
                output_end=i
                break

        for i in range(output_start,output_end+1):
            for j in range(0,len(contents[i].strip().strip('\n').split(','))):
                outputs.append((contents[i].strip().strip('\n')).split(',')[j])
            if(contents[i].strip().strip('\n')[-1] == ','):
                outputs.pop()

        if(';' in outputs[-1]):
            outputs[-1] = outputs[-1].replace(";","")     

        outputs[0]=outputs[0].split()[1].strip()


        for i in range(len(outputs)):
            outputs[i] = outputs[i].strip()

        outputs_so_far = list(inputs)

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

        N = 0

        for i in range(gate_start,gate_end+1):
            if ';' in contents[i]:
                N = N + 1


    ############################################################ Reading delay values from SDF File ############################
        file2 = open(sdf_file_path,"r")
        contents2 = file2.readlines()
        timing_array = np.zeros(shape =(3,6),dtype = object)
        delays_array = np.zeros(shape =(N,2,6),dtype = object)

        i = 0
        while "CELL" not in contents2[i]:
            i = i + 1

        line_containing_cell = i

        i = 0
        while(line_containing_cell <= len(contents2)-2):
            celltype = re.search('\"(.+)\"',contents2[line_containing_cell + 1]).group(1)
            instance_name = re.search('INSTANCE (.+)\)',contents2[line_containing_cell + 2]).group(1)
            instance_map[instance_name] = i
            
            if('INV' in celltype):
                no_of_inputs = 1
            else:
                no_of_inputs = int(re.search('.+(\d)LER.+',celltype).group(1))

            for j in range(no_of_inputs):
                timing_array[0,j] = re.search('IOPATH (.+) O .+',contents2[line_containing_cell + 4 + 1 + no_of_inputs + j]).group(1)
                timing_array[1:3,j] = re.findall(':(-?\d+)',contents2[line_containing_cell + 4 + 1 + no_of_inputs + j])

            timing_array[:,0:no_of_inputs] = timing_array[:,timing_array[0,0:no_of_inputs].argsort()]
            delays_array[i,:,:] = timing_array[1:3,:].astype(int)
            i = i + 1
            line_containing_cell = line_containing_cell + 4 + 2 * no_of_inputs + 3 + 1
            #print(delays_array)
            timing_array.fill(0)
        #print(delays_array)
                           

        
    ################################################################ End of reading delay values #####################

        to_be_checked=list(range(N))
        gates_arrival_time = np.zeros(shape=(N + 1 , 2), dtype = int)
        gate_arrival_time_summary = np.zeros(shape = (N,3), dtype = int)
        index_of_max_min_in_arrival_times = np.zeros(shape = (N,2) , dtype = object)
        node_level = np.zeros(shape = N+1, dtype = int)
        instance_name = []

        for i in inputs:
            output_node_map[i] = N  

        i =gate_start
        j = 0
        flag = 1
        while i <= gate_end:
            instance_name.append(contents[i].split('(')[0].split()[1].strip())
            words = re.search('\((.+)\)',contents[i]).group().strip('(')
            words_check = re.search('\((.+)',contents[i]).group()
           
            if ";" not in contents[i]:
                temp1 = contents[i+1].strip()
                words_check = words_check + temp1
                words = words + temp1
            words_check = words_check.strip('\(')
            
            words_check = words_check.split(',')
            
            for u in range(len(words_check)):
                words_check[u] = words_check[u].strip()
            words_check.sort()
    #            print(words_check)
            words_check.insert(0,words_check.pop())

            for k in range(len(words_check)):

                text = re.findall('\(([^)]+)',words_check[k])
                in_outs_of_this_gate.append(text[0])
            for s in range(len(in_outs_of_this_gate)):
                in_outs_of_this_gate[s] = in_outs_of_this_gate[s].strip()

            in_outs.append(in_outs_of_this_gate)
            no_of_inputs = len(in_outs[j]) - 1
            output_node_map[in_outs[j][0]] = j

            for f in in_outs[j][1:]:
                if f not in inputs:
                    flag = 0
                    break
            if(flag):
                gates_arrival_time[j,0] = np.amin(delays_array[instance_map[instance_name[j]],:,0:no_of_inputs])
                gates_arrival_time[j,1] = np.amax(delays_array[instance_map[instance_name[j]],:,0:no_of_inputs])
                node_level[j] = 1
                current_gates.append(j)
                to_be_checked.remove(j)
                outputs_so_far.append(in_outs[j][0].strip())
                
            flag = 1

            if ";" not in contents[i]:
                i = i + 1

            i = i+1
            j = j+1
            in_outs_of_this_gate = []

        flag = 1
        level = 2
        while(current_gates):
            for i in current_gates:
                for j in to_be_checked:

                    if(in_outs[i][0].strip() in in_outs[j][1:]):

                        for k in in_outs[j][1:]:
                            if k not in outputs_so_far:
                                flag = 0
                                break

                        if(flag):
                            if j not in current_gates_temp:

                                current_gates_temp.append(j)

                    flag = 1
                    
            current_gates = list(current_gates_temp)
            for u in current_gates_temp:
                to_be_checked.remove(u)
                outputs_so_far.append(in_outs[u][0])

            current_gates_temp = []

            for i in current_gates:
                gates_connected_to_input = itemgetter(*in_outs[i][1:])(output_node_map)
                no_of_inputs = len(in_outs[i][1:])
                min_among_min_input_arrival_times = np.amin(gates_arrival_time[gates_connected_to_input,0])
                max_among_min_input_arrival_times = np.amax(gates_arrival_time[gates_connected_to_input,0])
                max_among_max_input_arrival_times = np.amax(gates_arrival_time[gates_connected_to_input,1])
                index_of_min_among_min = np.where(gates_arrival_time[gates_connected_to_input,0] == min_among_min_input_arrival_times)
                index_of_max_among_min = np.where(gates_arrival_time[gates_connected_to_input,0] == max_among_min_input_arrival_times)
                index_of_max_among_max = np.where(gates_arrival_time[gates_connected_to_input,1] == max_among_max_input_arrival_times)

                gate_arrival_time_summary[i,0] = max_among_max_input_arrival_times - min_among_min_input_arrival_times
                gate_arrival_time_summary[i,1] = np.amin(delays_array[instance_map[instance_name[i]],:,index_of_min_among_min])
                #print(gate_arrival_time_summary[i,1],i)
                if (gate_arrival_time_summary[i,1] >= gate_arrival_time_summary[i,0]):
                    gate_arrival_time_summary[i,2] = 0
                else:
                    gate_arrival_time_summary[i,2] = 1
                    
                index_of_max_min_in_arrival_times[i,0] = index_of_min_among_min[0]
                index_of_max_min_in_arrival_times[i,1] = index_of_max_among_max[0]

                node_level[i] = level
                
                gates_arrival_time[i,0] = max_among_min_input_arrival_times + np.amin(delays_array[instance_map[instance_name[i]],:,0:no_of_inputs])
                gates_arrival_time[i,1] = max_among_max_input_arrival_times + np.amax(delays_array[instance_map[instance_name[i]],:,0:no_of_inputs])

                 

            level = level + 1
        summary_to_be_printed = np.zeros(shape = (N,5),dtype = int)
        summary_to_be_printed[:,0:3] = gate_arrival_time_summary
        #print("geronimooooo")
        #print(instance_map)
        #print(instance_name)
        #print("output_node_map = ",output_node_map)
        for i in range(N):
            if (isinstance(itemgetter(*in_outs[i][1:])(output_node_map),tuple)):
                summary_to_be_printed[i,3] = np.amin(node_level[list(itemgetter(*in_outs[i][1:])(output_node_map))])
                summary_to_be_printed[i,4] = np.amax(node_level[list(itemgetter(*in_outs[i][1:])(output_node_map))])
            else:
                summary_to_be_printed[i,3] = np.amin(node_level[itemgetter(*in_outs[i][1:])(output_node_map)])
                summary_to_be_printed[i,4] = np.amax(node_level[itemgetter(*in_outs[i][1:])(output_node_map)])

        #print(summary_to_be_printed[:,3:5])
        #np.savetxt('c1908_summary.csv',summary_to_be_printed,delimiter=',',fmt='%d',header='Maximum Arrival Time Difference,Minimum delay of gate,Potential for glitches,Minimum level of inputs,Maximum level of inputs'
        #           ,comments = '')

        summary_to_be_returned = summary_to_be_printed
        return summary_to_be_returned
                
    except IOError:
        print("Netlist file not found")

if __name__ == "__main__":
    result = timing_analysis(netlist_file_path,sdf_file_path)
    
	
       
            


#### All interpolation outputs are placed at bottom compared to v2

import atkr_writing_library_file as wf
#import writing_library_file as wf
import re
from pylab import *
from scipy.interpolate import interp1d as inp
from tkinter import *

def main(gate_name,gate_sizes,input_file,destination_file):
    file=open(input_file,"r")
    contents=file.readlines()

#    gate_name = "INVLERMX"
    expression = "\(" + gate_name + "[^0]"
    parameters = []
    parameters.append("POWER_7x7")
    parameters.append("cell_rise")
    parameters.append("rise_transition")
    parameters.append("cell_fall")
    parameters.append("fall_transition")

    k=[] #to hold line number of invlermx* gates
    flag_isxorxnor = 0
    for i in range(0,len(contents)):
        if re.search(expression,contents[i]):
             k.append(i)
    gate_list=np.zeros(shape=(len(k),2),dtype=int)

    gate_list[:,0] = k #gate_list array holds line number of invlermx* gates and their corresponding sizes


    for i in range(0,len(k)):
        gate_list[i,1] = int(re.search(gate_name + "(.*)\)",contents[k[i]]).group(1))

    gate_list = gate_list[gate_list[:,1].argsort()] # sorting based on sizes(smallest to largest)

#    if expression[2].isdigit():
    # atkr modified
    if gate_name == "INVLERMX":
        no_of_inputs = 1
        tc = no_of_inputs #timecount / library
        pc = no_of_inputs #powercount /library
    elif ("XOR" in gate_name or "XNR" in gate_name):
        flag_isxorxnor = 1  
        no_of_inputs = int(gate_name[3])
        tc = no_of_inputs* ( 1 + 2** (no_of_inputs-1) ) 
        pc = 2** no_of_inputs
    else:	
        no_of_inputs = int(gate_name[2])
        tc = no_of_inputs
        pc = no_of_inputs
    
    rc = (pc+4*tc)  #repetition_count: total number of parameters when they are all arranged next to next to each other
    timing_count = np.ndarray(shape=(tc,2,len(k)),dtype=object) 
    power_count  = np.ndarray(shape=(pc,2,len(k)),dtype=object)
    parameter_startpos = [0, pc, pc+1*tc, pc+2*tc, pc+3*tc] # {"power"{...upto pc}, "cell_rise"{....upto tc}, "transition_rise"{.... upto tc}.....}

    timing_text = []
    power_text = []

    for i,j in enumerate(gate_list[:,0]): #to get the line numbers of internal_power() and timing() with in the library models
        line_number = j
        input_counter_power = 0
        input_counter_timing = 0
        while not bool(re.search("input",contents[line_number])):
            if re.search("internal_power\(\)",contents[line_number]):
                 power_count[input_counter_power,0,i]=str(line_number)
                 power_count[input_counter_power,1,i]=contents[line_number+1].split("\"")[1]
                 input_counter_power = input_counter_power + 1
            else:
                if re.search("timing\(\)",contents[line_number]):
                    timing_count[input_counter_timing,0,i]=str(line_number)
                    timing_count[input_counter_timing,1,i]=contents[line_number+1].split("\"")[1]
                    input_counter_timing = input_counter_timing + 1
            line_number = line_number + 1

    #for i in range(len(k)):
        #power_count[:,:,i]=power_count[[power_count[:, 1, i].argsort()],:,i]
        #timing_count[:,:,i]=timing_count[[timing_count[:, 1, i].argsort()],:,i]

    parameter_value = np.ndarray(shape=(7*len(k),7*rc))
    output_capacitance = np.ndarray(shape=(len(k),7*rc))
    input_slew = np.ndarray(shape=(len(k),7*rc))
    max_capacitance = np.ndarray(shape=(len(k)),dtype=object)

    for i,j in enumerate(gate_list[:,0]):
        line = j
        while not bool(re.search("max_capacitance",contents[line])):
            line = line + 1
        function = contents[line - 2].split("\"")[1]
        max_capacitance[i] = float(contents[line].strip(';\n').split(':')[1].strip())
     
        marker = 0 #holds the correponding position
        power_text = []  
        for m in power_count[:,0,i]:
                m = int(m) + flag_isxorxnor # one line difference between xor and non-xors
                if flag_isxorxnor:
                    power_text.append(contents[m]+contents[m+1])
                else:
                    power_text.append(contents[m+1])
                output_capacitance[i,marker*7:(marker+1)*7] = np.array(contents[m+4].split("\"")[1].split(","),dtype=np.float64)  #35 is repetition_count
                input_slew[i,marker*7:(marker+1)*7] = np.array(contents[m+3].split("\"")[1].split(","),dtype=np.float64)
                for p in range(0,7):
                    parameter_value[i*7+p,marker*7:(marker+1)*7]= np.array(contents[m+p+5].split("\"")[1].split(","),dtype=np.float64)
                marker = marker + 1
        timing_text = []
        for m in timing_count[:,0,i]:
                for q in range(1,len(parameters)):
                    line = int(m)+1
                    current_timing_text = ''
                    while not bool(re.search(parameters[q],contents[line])):
                        if q == 1: current_timing_text = current_timing_text + contents[line]
                        line = line + 1
                    if q == 1: timing_text.append(current_timing_text)
                    output_capacitance[i,marker*7:(marker+1)*7]= np.array(contents[line+2].split("\"")[1].split(","),dtype=np.float64)
                    input_slew[i,marker*7:(marker+1)*7]= np.array(contents[line+1].split("\"")[1].split(","),dtype=np.float64)
                    for p in range(0,7):
                        parameter_value[i*7+p,marker*7:(marker+1)*7]= np.array(contents[line+p+3].split("\"")[1].split(","),dtype=np.float64)
                    marker = marker + 1


    no_of_gates_selected = len(k)
    gates_selected = range(no_of_gates_selected)

    flattened_parameters = np.ndarray(shape=((7*7)*rc,no_of_gates_selected))

    for i,j in enumerate(gates_selected):
        for l in range(rc):
            flattened_parameters[(7*7)*l:(7*7)*(l+1),i] = parameter_value[j*7:(j+1)*7,l*7:(l+1)*7].flatten()

    inp_parameters = [[None] for l in range(rc)]
    inp_output_capacitance = [[None] for l in range(rc)]
    inp_input_slew = [[None] for l in range(rc)]

    for i in range(rc):
        inp_parameters[i] = inp(gate_list[gates_selected,1],flattened_parameters[49*i:49*(i+1),:],fill_value='extrapolate')
        inp_output_capacitance[i] = inp(gate_list[gates_selected,1],output_capacitance[:,7*i:7*(i+1)],fill_value='extrapolate',axis=0)
        inp_input_slew[i] = inp(gate_list[gates_selected,1],input_slew[:,7*i:7*(i+1)],fill_value='extrapolate',axis=0)



    y_test = np.ndarray(shape=(7*7,rc))
    output_capacitance_test = np.ndarray(shape=(7,rc))
    input_slew_test = np.ndarray(shape=(7,rc))
    pin_capacitance_test =np.ndarray(shape=(no_of_inputs,1))
    leakage_power_test = np.ndarray(shape=(2**no_of_inputs,1))

    pin_capacitance = np.ndarray(shape=(no_of_gates_selected,no_of_inputs))
    cell_area = np.ndarray(shape=(no_of_gates_selected))
    cell_leakage_power = np.ndarray(shape=(no_of_gates_selected))
    leakage_power = np.ndarray(shape=(2**no_of_inputs,no_of_gates_selected))
    leakage_power_text = np.ndarray(shape=(2**no_of_inputs),dtype=object)


    for i,j in enumerate(gate_list[gates_selected,0]):
        line_number = j
        cell_area[i] = float(contents[line_number+1].strip(';\n').split(':')[1])
        cell_leakage_power[i] = float(contents[line_number+3].strip(';\n').split(':')[1])
        leakage_power_index = line_number + 4
        for u in range(0,2**no_of_inputs):
            leakage_power[u,i] = float(contents[leakage_power_index + 4*u + 2].strip(';\n').split(':')[1])
            leakage_power_text[u] = contents[leakage_power_index + 4*u + 1].strip(';\n').split(':')[1].strip()
        for m in range(no_of_inputs):
            while not bool(re.search("pin\(I{}\)".format(m+1),contents[line_number])):
                line_number = line_number + 1
            pin_capacitance[i,m] = float(contents[line_number+2].strip(';\n').split(':')[1].strip())

    inp_pin_capacitance = [None] * no_of_inputs
    inp_cell_area = [None]
    inp_cell_leakage_power = [None]
    inp_leakage_power = [None] * (2**no_of_inputs)
    inp_max_capacitance = [None]

    for i in range(no_of_inputs):
        inp_pin_capacitance[i] = inp(gate_list[gates_selected,1],pin_capacitance[:,i],axis=0,fill_value='extrapolate')


    inp_cell_area = inp(gate_list[gates_selected,1],cell_area,fill_value='extrapolate')
    inp_cell_leakage_power = inp(gate_list[gates_selected,1],cell_leakage_power,fill_value='extrapolate')
    inp_max_capacitance = inp(gate_list[gates_selected,1],max_capacitance,fill_value='extrapolate')

    

    
    for x_test in gate_sizes:
        for i in range(rc):
            y_test[:,i] = inp_parameters[i](x_test)
            output_capacitance_test[:,i]=inp_output_capacitance[i](x_test)
            input_slew_test[:,i]=inp_input_slew[i](x_test)

        for i in range(no_of_inputs):
            pin_capacitance_test[i,0]=inp_pin_capacitance[i](x_test)

        for i in range(0,2**no_of_inputs):    
            inp_leakage_power[i] = inp(gate_list[gates_selected,1],leakage_power[i,:],fill_value='extrapolate')
            leakage_power_test[i] = np.around(inp_leakage_power[i](x_test))

        cell_area_test = inp_cell_area(x_test)
        cell_leakage_power_test = np.around(inp_cell_leakage_power(x_test))
        max_capacitance_test = inp_max_capacitance(x_test)
        #breakpoint()
        wf.write_file(gate_name,x_test,cell_area_test,cell_leakage_power_test,no_of_inputs,leakage_power_text,max_capacitance_test,input_slew_test,output_capacitance_test,\
                      y_test,pin_capacitance_test,power_count,leakage_power_test,parameters,function,destination_file,power_text,timing_text)
        
#    return gate_name,x_test,cell_area_test,cell_leakage_power_test,no_of_inputs,leakage_power_text,max_capacitance_test,input_slew_test,output_capacitance_test,y_test,pin_capacitance_test,power_count,leakage_power_test,parameters

if __name__ == '__main__':
    main()



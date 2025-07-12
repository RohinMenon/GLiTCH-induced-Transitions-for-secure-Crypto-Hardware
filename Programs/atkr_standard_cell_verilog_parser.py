from pylab import *
from scipy.interpolate import interp1d as inp
import atkr_writing_verilog_file as wf
#import writing_verilog_file as wf

def main(gate_name,gate_sizes,input_file,destination_file):
    file=open(input_file,"r")
    contents=file.readlines()

    #gate_name = "ND2LERMX"
    expression = "\s" + gate_name + "[^0]"

    k=[] #to hold line number of invlermx* gates

    for i in range(0,len(contents)):
        if re.search(expression,contents[i]):
             k.append(i)

    gate_list=np.zeros(shape=(len(k),2),dtype=int)

    gate_list[:,0] = k #gate_list array holds line number of invlermx* gates and their corresponding sizes

    no_of_gates = len(k)
    for i in range(0,no_of_gates):
        gate_list[i,1] = int(re.search(gate_name + "(.*)\)",contents[k[i]]).group(1).split('(')[0])

    gate_list = gate_list[gate_list[:,1].argsort()] # sorting based on sizes(smallest to largest)



 
    output_line = contents[gate_list[0,0]+1]
    input_line = contents[gate_list[0,0]+2]
    output_input_list = re.search(gate_name + "(.*)\)",contents[gate_list[0,0]]).group(1).split('(')[1].strip(');\n')
    function_line = []
    path_delay_descriptions = []

    line_number = gate_list[0,0]
    while not bool(re.search("protect",contents[line_number])):
        line_number = line_number + 1
    line_number = line_number + 1
    while not bool(contents[line_number] == '\n'):
        function_line.append(contents[line_number].strip())
        line_number = line_number + 1
        
    line_number = gate_list[0,0]
    while not bool(re.search("specify",contents[line_number])):
        line_number = line_number + 1
    line_number = line_number + 3
    
    while not bool(re.search("endspecify",contents[line_number])):
        path_delay_descriptions.append(contents[line_number].split(' = ')[0].strip())
        line_number = line_number + 1
       
    no_of_inputs = len(output_input_list.split(',')) - 1
    #atkr modified to accomodate xor/xnor gate
    if('XOR' in gate_name or 'XNR' in gate_name):
        no_of_delay_values = no_of_inputs * ( 1 + 2**(no_of_inputs-1))
    else:
        no_of_delay_values = no_of_inputs
    rise_delay = np.ndarray(shape=(no_of_delay_values,no_of_gates))
    fall_delay = np.ndarray(shape=(no_of_delay_values,no_of_gates))

    for i,j in enumerate(gate_list[:,0]):
        line_number = j
#        print(contents[line_number])
        while not bool(re.search("specify",contents[line_number])):
            line_number = line_number + 1
        for u in range(no_of_delay_values):
#            print(contents[line_number + 3 + u].split('=')[1].split(',')[0].strip().strip('(').split(':')[0])
#            print('\n')
            rise_delay[u,i] = float(contents[line_number + 3 + u].split(' = ')[1].split(',')[0].strip().strip('(').split(':')[0])
            fall_delay[u,i] = float(contents[line_number + 3 + u].split(' = ')[1].split(',')[1].strip('(').split(':')[0])

    inp_rise_delay = [None] * no_of_delay_values
    inp_fall_delay = [None] * no_of_delay_values
    rise_delay_test = np.ndarray(shape=(no_of_delay_values),dtype=np.float64)
    fall_delay_test = np.ndarray(shape=(no_of_delay_values),dtype=np.float64)

    for i in range(no_of_delay_values):
        inp_rise_delay[i] = inp(gate_list[:,1],rise_delay[i,:],fill_value='extrapolate')
        inp_fall_delay[i] = inp(gate_list[:,1],fall_delay[i,:],fill_value='extrapolate')
#    x_test = float(full_gate_name[8:])
    for x_test in gate_sizes:
        for i in range(no_of_delay_values):
            rise_delay_test[i] = np.around(inp_rise_delay[i](x_test),5)
            fall_delay_test[i] = np.round(inp_fall_delay[i](x_test),5)
        wf.write_file(gate_name,output_line,input_line,output_input_list,function_line,path_delay_descriptions,rise_delay_test,\
        fall_delay_test,x_test,no_of_inputs,destination_file)       
#    return gate_name,output_line,input_line,output_input_list,function_line,path_delay_descriptions,rise_delay_test,\
#    fall_delay_test,x_test,no_of_inputs 






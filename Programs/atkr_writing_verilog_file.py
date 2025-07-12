import re

def write_file(gate_name,output_line,input_line,output_input_list,function_line,path_delay_descriptions,
               rise_delay_test,fall_delay_test,x_test,no_of_inputs,destination_file):

    #atkr modified to accomodate xor/xnor gate
    if('XOR' in gate_name or 'XNR' in gate_name):
        no_of_delay_values = no_of_inputs * ( 1 + 2**(no_of_inputs-1))
    else:
        no_of_delay_values = no_of_inputs

    with open(destination_file,'a') as f:
        f.write("`resetall\n")
        f.write("`timescale 10ps/1ps\n")
        f.write("`celldefine\n")
        size = x_test
        if re.search(".",str(x_test)):
            size = re.sub("\.","dot",str(x_test))
        f.write("module {}{}({});\n".format(gate_name,size,output_input_list))
        f.write(output_line)
        f.write(input_line)
        f.write("\n")
        f.write("`protect\n")
        for i in range(len(function_line)):
            f.write(function_line[i]+"\n")
        f.write("\n")
        f.write("{:>{}}".format("specify",len("specify")+3))
        f.write("\n")
        for i in range(no_of_delay_values):
            string= "{0} = ({1}:{1}:{1}, {2}:{2}:{2});\n"
            f.write("{:>{}}".format(string.format(path_delay_descriptions[i],rise_delay_test[i],fall_delay_test[i]),len(string.format(path_delay_descriptions[i],rise_delay_test[i],fall_delay_test[i]))+6))
        f.write("{:>{}}\n".format("endspecify",len("endspecify")+3))
        f.write("`endprotect\n")
        f.write("endmodule\n")
        f.write("`endcelldefine\n")
        f.write("\n")
        f.write("\n")

 

import re

def write_file(gate_name,x_test,cell_area_test,cell_leakage_power_test,no_of_inputs,leakage_power_text,max_capacitance_test,input_slew_test,output_capacitance_test,y_test,pin_capacitance_test,power_count,leakage_power_test,
               parameters,function,destination_file,power_text,timing_text):
    
    parameters_to_write = list(["power(POWER_7x7)","cell_rise(DELAY_7x7)","rise_transition(DELAY_7x7)","cell_fall(DELAY_7x7)","fall_transition(DELAY_7x7)"])
    flag_isxorxnor = 1 if ("XOR" in gate_name or "XNR" in gate_name) else 0
    if "INV" in gate_name:
        inputs = re.findall(r'I',function)
    else:
        inputs = re.findall(r'I\d+',function)


    with open(destination_file,'a') as f:

        f.write("\n")
        size = x_test
        if re.search(".",str(x_test)):
            size = re.sub("\.","dot",str(x_test))
        f.write("cell({}) {{\n".format(gate_name + size))
        string = "area : {:7.6f};"
        f.write("{:>{}}\n".format(string.format(cell_area_test),len(string.format(cell_area_test))+2))
        string = "cell_footprint : \"{}\" ;"
        f.write("{:>{}}\n".format(string.format(gate_name[0:3]),len(string.format(gate_name[0:3]))+2))
        string ="cell_leakage_power : {} ;"
        f.write("{:>{}}\n".format(string.format(cell_leakage_power_test),len(string.format(cell_leakage_power_test))+2))
        for i in range(2**no_of_inputs):
            string = "leakage_power() {"
            f.write("{:>{}}\n".format(string,2))
            string = "when : {};"
            f.write("{:>{}}\n".format(string.format(leakage_power_text[i]),len(string.format(leakage_power_text[i]))+4))
            string="value : {};"
            f.write("{:>{}}\n".format(string.format(leakage_power_test[i,0]),len(string.format(leakage_power_test[i,0]))+2))
            string="}"
            f.write("{:>{}}\n".format(string,len(string)+2))
        string = "pin(O) {"
        f.write("{:>{}}\n".format(string,len(string)+2))
        string = "function : \"{}\";".format(function)
        f.write("{:>{}}\n".format(string,len(string)+4))
        string="direction : output ;"
        f.write("{:>{}}\n".format(string,len(string)+4))
        string="max_capacitance : {:7.6f};"
        f.write("{:>{}}\n".format(string.format(max_capacitance_test),len(string.format(max_capacitance_test))+4))
       
        if flag_isxorxnor:
            iteratorPower = 2**no_of_inputs
            iteratorTime  = no_of_inputs * ( 1 + 2**(no_of_inputs-1))
        else:
            iteratorPower = no_of_inputs
            iteratorTime = no_of_inputs
 
        rc = -1
        for i in range(iteratorPower):
            rc = rc + 1
            string = "internal_power() {"
            f.write("{:>{}}\n".format(string,len(string)+4))
            f.write(power_text[i])
            string = parameters_to_write[0] + " {"
            f.write("{:>{}}\n".format(string,len(string)+6))
            string="index_1(\""
            for m in range(7):
                string = string + "{:7.6f},".format(input_slew_test[m,rc])
            string = string[:-1]
            string = string + "\");"
            f.write("{:>{}}\n".format(string,len(string)+8))
            string="index_2(\""
            for m in range(7):
                string = string + "{:7.6f},".format(output_capacitance_test[m,rc])
            string = string[:-1]
            string = string + "\");"
            f.write("{:>{}}\n".format(string,len(string)+8))
            string="values(\""
            for m in range(7):
                string = string + "{:7.6f},".format(y_test[m,rc])
            string = string[:-1]
            string = string + "\",\\"
            f.write("{:>{}}\n".format(string,len(string)+8))
            for j in range(1,7):
                string="\""
                for m in range(7):
                    string = string + "{:7.6f},".format(y_test[j*7+m,rc])
                string =string[:-1]
                if j!=6:
                    string = string+"\",\\"
                    f.write("{:>{}}\n".format(string,len(string)+8+len("values(\"")))
                else:
                    string = string+"\");"
                    f.write("{:>{}}\n".format(string,len(string)+8+len("values(\"")))
                    
            f.write("{:>{}}\n".format("}",len("}")+6))
            f.write("{:>{}}\n".format("}",len("}")+4))

        for i in range(iteratorTime):
            string = "timing() {"
            f.write("{:>{}}\n".format(string,len(string)+4))
            f.write(timing_text[i])
            for j in range(1,len(parameters)):
                rc = rc + 1
                string = parameters_to_write[j] + " {"
                f.write("{:>{}}\n".format(string,len(string)+6))
                string="index_1(\""
                for m in range(7):
                    string = string + "{:7.6f},".format(input_slew_test[m,rc])
                string = string[:-1]
                string = string + "\");"
                f.write("{:>{}}\n".format(string,len(string)+8))
                string="index_2(\""
                for m in range(7):
                    string = string + "{:7.6f},".format(output_capacitance_test[m,rc])
                string = string[:-1]
                string = string + "\");"
                f.write("{:>{}}\n".format(string,len(string)+8))
                string="values(\""
                for m in range(7):
                    string = string + "{:7.6f},".format(y_test[m,rc])
                string = string[:-1]
                string = string + "\",\\"
                f.write("{:>{}}\n".format(string,len(string)+8))
                for p in range(1,7):
                    string="\""
                    for m in range(7):
                        string = string + "{:7.6f},".format(y_test[p*7+m,rc])
                    string =string[:-1]
                    if p!=6:
                        string = string+"\",\\"
                        f.write("{:>{}}\n".format(string,len(string)+8+len("values(\"")))
                    else:
                        string = string+"\");"
                        f.write("{:>{}}\n".format(string,len(string)+8+len("values(\"")))
                    
                f.write("{:>{}}\n".format("}",len("}")+6))
            f.write("{:>{}}\n".format("}",len("}")+4))
        f.write("{:>{}}\n".format("}",len("}")+2))

        for i in range(no_of_inputs):
            string="pin({}) {{"
            f.write("{:>{}}\n".format(string.format(inputs[i]),len(string.format(inputs[i]))+2))
            string="direction : input ;"
            f.write("{:>{}}\n".format(string,len(string)+4))
            string="capacitance : {:7.6f}"
            f.write("{:>{}}".format(string.format(pin_capacitance_test[i,0]),len(string.format(pin_capacitance_test[i,0]))+4))
            f.write(";\n")
            f.write("{:>{}}\n".format("}",len("}")+2))
        f.write("}\n")
        f.write("\n")

if __name__ == '__main__':
    main()

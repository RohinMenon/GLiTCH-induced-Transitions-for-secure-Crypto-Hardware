import re


gate_dict = {"ND":"nand", "NR":"nor", "IN":"not", "DL":"not", "TI":"not", "XN":"xnor", "XO":"xor"}


#D:\IIT New\Research\demo_computeGlitchCriticalityMetric/inputs/priority_netlist.v
file_name = "priority_netlist.v"
write_file_name = "priority_tmp"
def temp_file_generator(circuit_name,netlist_file_path):
        file_name = netlist_file_path + circuit_name + "_netlist.v"
        write_file_name = netlist_file_path + circuit_name + "_tmp"
        with open(write_file_name,'w') as w:
                with open(file_name,'r') as f:
                    contents = f.readlines()
                    for i in range(len(contents)):            
                        if "wire" in contents[i]:
                            wire_end = i
                        if "endmodule" in contents[i]:
                            gate_end = i - 1

                    while ';' not in contents[wire_end]:
                        wire_end = wire_end + 1


                        
                    gate_start = wire_end + 1
                    i = gate_start
                    while i <= gate_end:
                        current_line = contents[i]
                        words = re.search('\((.+)',contents[i]).group().strip('(')
                        words_check = re.search('\((.+)',contents[i]).group()

                        if ';' not in contents[i]:
                            words = words + contents[i+1].strip()
                            words_check = words_check.strip('\n') + contents[i+1].strip()
                            i = i + 1

                        words_check = words_check.strip('\(')
                        words_check = words_check.split(',')

                        input_labels = re.findall('\.[^(]+',words)
                        for z in range(len(input_labels)):
                            input_labels[z] = input_labels[z].strip().strip('.')

                        string = current_line.split()[0][0:2]
                        string = gate_dict[string] + str(len(words_check)-1) + ' ' + current_line.split('(')[0].split()[1] + ' '
                        string = re.sub("not1","inv",string)
                        w.write(string)

                        string = ""
                        for k in range(len(words_check)):
                            text = re.findall('\(([^)]+)',words_check[k])
                            string = string + input_labels[k] + ':' + '\'' + text[0] + '\'' + ' '
                        string = string[:-1]
        #            print(string)
                        w.write(string)
                        w.write('\n')
                        i = i + 1

                
            


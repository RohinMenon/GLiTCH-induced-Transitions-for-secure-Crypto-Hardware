import numpy as np
import gate_name_gen as gng
import atkr_standard_cell_verilog_parser as verilog_psr
#import standard_cell_verilog_parser as verilog_psr
import atkr_library_parser_v3_all_gates_selected as lib_psr
#import library_parser_v3_all_gates_selected as lib_psr
import generate_verilog_source as gvs

def generate_library_and_netlist_files( run_mode,
                                        path_final,
                                        netlist_file,
                                        source_verilog_write_file,
                                        verilog_input_file,
                                        verilog_destination_file,
                                        library_input_file,
                                        library_destination_file):

    generated_sizes = np.loadtxt(path_final + f"/{run_mode}sizes.txt")

    gate_name,gate_sizes = gng.main(netlist_file,generated_sizes)
    gvs.main(generated_sizes,source_verilog_write_file,netlist_file)

    with open(library_input_file,'r') as f:
        contents = f.readlines()
        with open(library_destination_file,'a') as f1:    
            i=0
            while "cell(" not in contents[i]:
                f1.write(contents[i])
                i = i + 1

    for i,k in zip(gate_name,gate_sizes):
        verilog_psr.main(i,k,verilog_input_file,verilog_destination_file)
        lib_psr.main(i,k,library_input_file,library_destination_file)

    with open(library_destination_file,'a') as f1:
        f1.write("}")
    
    return 0

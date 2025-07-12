import re
import numpy as np
import os


#circuit_name = "c2670"
#AM_run_number = 187

def sdf_modify(circuit_name,AM_run_number):

        for m in range(1,3):
                if (m == 1):
                        run_number = AM_run_number
                elif (m == 2):
                        run_number = AM_run_number + 1

                sdf_in_file_full_path = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_2',circuit_name + f"_sizes{run_number}",circuit_name + '_results',circuit_name + '.sdf')
                sdf_out_file_full_path = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_2',circuit_name + f"_sizes{run_number}",circuit_name + '_results',circuit_name + '_avg.sdf')

                with open(sdf_out_file_full_path,'w') as out_file:
                        with open(sdf_in_file_full_path) as in_file:
                                contents = in_file.readlines()
                                i = 0

                                while("CELL\n" not in contents[i]):
                                        out_file.write(contents[i])
                                        i = i + 1

                                i = 0
                                while(True):
                                        while(i <= len(contents) - 1 and "CELL\n" not in contents[i]):
                                                i = i + 1
                                        if(i == len(contents)):
                                                break
                                        
                                        gate_type = re.search('\"(.+?)\"',contents[i+1]).group(1)
                                        if (gate_type[0:3] == "INV"):
                                                no_of_inputs = 1
                                        else:
                                                no_of_inputs = int(gate_type[2])

                                        delay_array = np.zeros(shape=(no_of_inputs,2))
                                        for j in range(no_of_inputs):
                                                rise_delay = int(re.findall('::(.+?)\)',contents[i + 5 + no_of_inputs + j])[0])
                                                fall_delay = int(re.findall('::(.+?)\)',contents[i + 5 + no_of_inputs + j])[1])
                                                delay_array[j,0] = rise_delay
                                                delay_array[j,1] = fall_delay

                                        avg = np.around(np.average(delay_array),decimals = 3)
                                        cell_details = contents[i]

                                        k = i + 1
                                        while (k <= len(contents) - 1 and "CELL\n" not in contents[k]):
                                                cell_details = cell_details + contents[k]
                                                k = k + 1
                                        cell_details = re.sub('::\d\d',f"::{avg}",cell_details)
                                        out_file.write(cell_details)

                                        i = i + 1
			
	
		
	

import sys
import numpy as np

def read_criticality_files(syn_criticality_file_path,out_criticality_file_path,N,in_out_list):
    criticality_dict = {}
    net_capacitance={}
    generated_glitch={}
    propagated_glitch={}
    criticality = np.zeros(shape=(N))
    glitch_array = np.zeros(shape=(3,N))
    
    try:
        file2 = open(syn_criticality_file_path,"r")
        criticality_file_contents = file2.readlines()


        for i in range(len(criticality_file_contents)):
            node = criticality_file_contents[i].split()[0].strip()
            criticality_dict[node] = float(criticality_file_contents[i].split()[1].strip())

        criticality = np.zeros(shape=(N))

        for i in range(N):
            try:
                criticality[i] = criticality_dict[in_out_list[i][0]]
            except KeyError:
                pass

    except IOError:
        print("criticality metric csv file not found in {}".format(syn_criticality_file_path))
        sys.exit(1)

    try:
        file3 = open(out_criticality_file_path,"r")
        glitch_file_contents = file3.readlines()
        for i in range(1,len(glitch_file_contents)):
            node = glitch_file_contents[i].split(',')[0].strip()
            net_capacitance[node] = float(glitch_file_contents[i].split(',')[3])
            generated_glitch[node] = float(glitch_file_contents[i].split(',')[4])
            propagated_glitch[node] = float(glitch_file_contents[i].split(',')[5])

        glitch_array = np.zeros(shape=(3,N))

        for i in range(N):
            try:
                glitch_array[0,i] = net_capacitance[in_out_list[i][0]]
                glitch_array[1,i] = generated_glitch[in_out_list[i][0]]
                glitch_array[2,i] = propagated_glitch[in_out_list[i][0]]
            except KeyError:
                pass
        glitch_array[1,:] = 1000*glitch_array[1,:]
        glitch_array[2,:] = 1000*glitch_array[2,:]
    except IOError:
        print("Glitch contents file not found in {}".format(out_criticality_file_path))
        sys.exit(1)

    return criticality,glitch_array

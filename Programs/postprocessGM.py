from pylab import *
def postprocessGM(N,sol,criticalgates,F,Glog,gate_output_wire_capacitance,Cref,Opsize,gate_type_list,parasiticDelay,input_stage_data,use_leakdata,thres=500) :
    '''
    I/p to function
    GSsol : solution of the gate-sizing optimization
    O/p of function
    critical : 
    '''
    GM_arrival_times = sol["variables"]["a"]
    GM_gate_sizes = sol["variables"]["x"]
    GM_gate_sizes_diagonal_matrix = diag(1/GM_gate_sizes)
    comparison = np.zeros(shape=(N,2))

    # Question : How is this correct?
    GM_inertial_delay = (F @ GM_gate_sizes + (gate_output_wire_capacitance/Cref) + Opsize)@ GM_gate_sizes_diagonal_matrix + array(list(parasiticDelay.values()))
    # Question : which of theseare correct
    #GM_inertial_delay = (F @ GM_gate_sizes + (gate_output_wire_capacitance/Cref) + Opsize)@ GM_gate_sizes_diagonal_matrix + array(list(parasiticDelay.values()))

    comparison[:,1] = GM_inertial_delay
    arrind = np.where(F!=0)
    Iparr = array([arrind[0][np.where(arrind[1] == i)] for i in range(0,N)])


    for i in range(N):
        if(Iparr[i].size != 0):
            if(gate_type_list[i] == "NOT1"):
                comparison[i,0] = 10101 #GM_arrival_times[Iparr[i][0]]
            else:
                comparison[i,0] = np.max(GM_arrival_times[Iparr[i][:]]) - np.min(GM_arrival_times[Iparr[i][:]])
    #print("Debug: postprocessGM(): comparison =",comparison)


    critical = np.zeros(N)
    for i in range(N):
        if(criticalgates[i] >= thres and gate_type_list[i]!='NOT1'):  # and comparison[i,0] < 10 * comparison[i,1]): and input_stage_data[i,1] - input_stage_data[i,0] <= 3 and criticalgates[i] >= thres and 
            critical[i] = 1
    if(not use_leakdata):
        print("Info: postprocessGM(): Number of critical gates are ",critical.sum(),"out of total ",N)


    #Powfrac = sum(sol["variables"]["x"])        #Power of sizing alone

    return critical,comparison

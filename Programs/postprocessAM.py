from pylab import *
import get_leaks
def postprocessAM(N,sol,leak_score,glitch_count,F,Glog,gate_output_wire_capacitance,Cref,Opsize,gate_type_list,parasiticDelay,maxGlitch,minGlitch) :
    '''
    I/p to function
    GSsol : solution of the gate-sizing optimization
    O/p of function
    critical : 
    '''
    AM_arrival_times = sol["variables"]["a"]
    AM_gate_sizes = sol["variables"]["x"]
    AM_gate_sizes_diagonal_matrix = diag(1/AM_gate_sizes)
    comparison = np.zeros(shape=(N,2))
    print(f"Debug: postprocessAM(): gateIndex to maximize glitch are {maxGlitch} ")
    print(f"Debug: postprocessAM(): gateIndex to minimize glitch are {minGlitch} ")

    
    #Question : How is this correct?
    AM_inertial_delay = (F @ AM_gate_sizes + Glog*(gate_output_wire_capacitance/Cref) + Glog*Opsize)@ AM_gate_sizes_diagonal_matrix + array(list(parasiticDelay.values()))
    comparison[:,1] = AM_inertial_delay
    arrind = np.where(F!=0)
    Iparr = array([arrind[0][np.where(arrind[1] == i)] for i in range(0,N)])
    for i in range(N):
        if(Iparr[i].size != 0):
            if(gate_type_list[i] == "NOT1"):
                comparison[i,0] = 10101 #AM_arrival_times[Iparr[i][0]]
            else:
                comparison[i,0] = np.max(AM_arrival_times[Iparr[i][:]]) - np.min(AM_arrival_times[Iparr[i][:]])

    critical = np.zeros((N,2))
    #for i in range(N):
    #    if(leak_score[i]<=leak_thres_uplimit and leak_score[i] >= leak_thres_downlimit and gate_type_list[i]!='NOT1'): 
    #        critical[i,1] = 1
    #    elif(glitch_count[i] >= glitch_thres and gate_type_list[i]!='NOT1'): 
    #        critical[i,0] = 1

    for i in maxGlitch:
        critical[i,0] = 1
    for i in minGlitch:
        critical[i,1] = 1
    print("Info: postprocessAM(): Number of glitch minimising critical gates are ",critical[:,1].sum(),"out of total ",N)
    print("Info: postprocessAM(): Number of glitch maximising critical gates are ",critical[:,0].sum(),"out of total ",N)

    Powfrac = sum(sol["variables"]["x"])        #Power of sizing alone
    return critical,Powfrac,comparison

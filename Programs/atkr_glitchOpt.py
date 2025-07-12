                                    #Import libraries
from pylab import *
from gpkit import VectorVariable, Variable, Model, units , exceptions
from gpkit.constraints.bounded import Bounded
from itertools import *
import random
from pickle import dump             #!pip install pickle-mixin :to install pickle
from pickle import load
import csv
import sys
import time
sys.setrecursionlimit(16000)

                                    #Glitch maximization

def glitchOptObj(AMsol,N,T0,F,Opsize,Glog,Iparr,indIparr,Ips,maxIp,gsPower,GSarrT,parasiticDelay,gate_output_wire_capacitance,Cref,input_depth,circuit_name,dont_consider_transition_time,inertialdelay_AM,critical,excessP_i,glitchExponent,maxGsize_i,Twall_i,inertial_delay_frac_i):
    auto_correction_factor = 1
    maxGsize = auto_correction_factor * maxGsize_i
    Twall_i = 1.25
    print("Twall is ", Twall_i)
    Twall = auto_correction_factor * Twall_i
    excessP = auto_correction_factor * excessP_i
    #inertial_delay_frac = inertial_delay_frac_i * auto_correction_factor
    inertial_delay_frac = inertial_delay_frac_i * 0.75
    maxGsize = 16
    #print("IPS ",Ips)
    #print("Iparr ",Iparr)
    '''
    I/p to function
    
    O/p of function
    '''
    print("Info: glitchMaxObj(): Calculating Glitch minimisation objective")
    print(f'Info: glitchMaxObj(): excessP {excessP_i}')
    cost_dict = {"c432": 1222982.0,"c880": 544093.5,"c1908": 131214.4,"c2670": 124713.6,"c3540": 1501226.0,"c5315":837555.0,"c6288":2212.771,"c7552":104595.5,"adder":7551.68,"barrel_shifter":50860.87}
    #alpha = 1
    #AM_sizes_sum = AMsol["variables"]["a"].sum()
                                    #Dynamic default

                                    #Declare Variablesconstraints = constraints + [Ts <= 1.1*T0]
    Gsize = VectorVariable(N,"x")   #Gate sizes
    Tarr = VectorVariable(N,"a")    #Arrival times
    Ts = Variable("Ts")             #Timing wall (used in TIMING MIN)
    X = diag(1/Gsize)               #Matrix used for computation
    time_objective = Variable("time_obj")
    area_objective = Variable("area_obj") 
    primary_gates = []
    modifiedGates = []
    minimise_criticalgates = []
    maximise_criticalgates = []
    criticalGateswithPI = []
    Tinparr =  0
    numberofminobj = 0
    numberofmaxobj = 0
    
                                    #Computations from initial data
    Fout = (F@ Gsize + gate_output_wire_capacitance/Cref + Opsize)@ X  #Fan out matrix (with o/p Cap)
    arrind = np.where(F!=0)                                            #Indices with non-zero 
    Iparr = array([arrind[0][np.where(arrind[1] == i)] for i in range(0,N)])    #Arrival time matrix    


    inertialdelay_GM = (F @ Gsize + Glog*(gate_output_wire_capacitance/Cref) + Glog*Opsize)@ X + array(list(parasiticDelay.values()))
                                    #Objective
    maximise_objective = 0
    minimise_objective = 0
    toprint,toprint2 = 0,0
    a1,a2 = 0,0
                                    #Equation writing
    gate_cnstr = []
    maximise_gate_cnstr = []
    minimise_gate_cnstr = []
    Gsize_noncritical = 0;
    AMGsize_noncritical = 0;
    Gsize_critical_withprimary = 0
    Gsize_critical = 0

    for n in range(0,N) :
                                    #Evaluate parasitic delay
        if Glog[n] != 1 :
            if Ips[n] == 1:
                print("Something is wrong")
            else :
                pass

        if not (critical[n,0]):         #Collect Data about non maximise-critical
            Gsize_noncritical = Gsize_noncritical+ Gsize[n]
            AMGsize_noncritical += AMsol["variables"]["x"][n]
 
        if Opsize[n] != 0 :         #For primary o/p constraint
            gate_cnstr.append(Tarr[n] <= Ts)
            
        if len(Iparr[n])!=0 :       #Arrival time contraints
            for i in range(0,len(Iparr[n])) :
                gate_cnstr.append(Tarr[n] >= Fout[n] + parasiticDelay[n] + Tarr[Iparr[n][i]])
           
                                    #Minimize arrival times of gates w/ primary inputs
            #if len(Iparr[n]) != Ips[n]:
                #gate_cnstr.append(Tarr[n] >= Fout[n] + parasiticDelay[n] + Tinparr) #Extra clause to include the input skews as to better optimise
                #for i in range(0,len(Iparr[n])) :
                    #if max(input_depth[n]) <= 100 and Glog[n]!=1 and critical[n,1]:
                        #Obj = critical[n,1]*(Tarr[Iparr[n][i]]**glitchExponent)#*(Gsize[n]) ## atkr commented
                        #minimise_objective = minimise_objective + Obj
                        #numberofminobj=numberofminobj+1
                        #print(f"Debug: glitchOptObj(): min {numberofminobj} obj is {Obj} for gate {n}")

            if len(Iparr[n]) >= 2 :
                if(critical[n,0]>0):#maximise_criticalgate
                    print(f'Debug: glitchOptObj(): {n} is under glitch maximisation')
                    maximise_criticalgates.append(n)
                    arrThres = ceil(len(Iparr[n])/2)
                    if arrThres >= 2 :  #Take those which have more than 3 inputs
                        inputset = np.argsort(GSarrT[Iparr[n]])
                        arrTset = list(inputset)[:int(floor(arrThres/2))] + list(inputset)[-int(ceil(arrThres/2)):]
                    else :              #For 2 input gates
                        arrTset = range(len(Iparr[n]))
                        inputset = range(len(Iparr[n]))
    
                    modifiedGates.extend(list(Iparr[n][arrTset]))
                    temp = combinations(arrTset,2)
                    ipcomb = array(list(temp))
                    nArr = n*np.ones(shape(ipcomb)).astype(int)
                   
 		            #Glitch objective as ratio of array
                    glObj = Tarr[indIparr[nArr,ipcomb]]
                    ratioObj = glObj[:,1]/glObj[:,0]  #amore/aless 
                    #glitch maximization constraint 
                    myGlitchArrivalConstraint = (glObj[:,0]  + inertial_delay_frac * inertialdelay_GM[n])/glObj[:,1] #atkr constraint
                    if myGlitchArrivalConstraint.any() !=0:
                       maximise_gate_cnstr.append(myGlitchArrivalConstraint <= 1)
                       #print(f"Debug: glitchOptObj(): maxcnstr: {myGlitchArrivalConstraint}<=1 for gate {n}")
                       #maximise_gate_cnstr.append(ratioObj >= 1)
                    Obj = pow(ratioObj,-1*glitchExponent)
                    numberofmaxobj = numberofmaxobj + 1
                    maximise_objective = maximise_objective + sum(Obj)    
                    #print(f"Debug: glitchOptObj(): max {numberofmaxobj} obj is {sum(Obj)} for gate {n}")
 
                if(critical[n,1]>0): #minimise_criticalgate
                    print(f'Debug: glitchOptObj(): {n} is under glitch minimisation')
                    minimise_criticalgates.append(n)
                    arrThres = ceil(len(Iparr[n])/2)
                    if arrThres >= 2 :  #Take those which have more than 3 inputs
                        #print(f'Debug: glitchMaxObj(): Iparr[{n}] {Iparr[n]}')
                        inputset = np.argsort(GSarrT[Iparr[n]])
                        arrTset = list(inputset)[:int(floor(arrThres/2))] + list(inputset)[-int(ceil(arrThres/2)):]
                    else :              #For 2 input gates
                        arrTset = range(len(Iparr[n]))
                        inputset = range(len(Iparr[n]))
    
                    modifiedGates.extend(list(Iparr[n][arrTset]))
                    temp = combinations(arrTset,2)
                    ipcomb = array(list(temp))
                    nArr = n*np.ones(shape(ipcomb)).astype(int)
                   
 		            #Glitch objective as ratio of array
                    glObj = Tarr[indIparr[nArr,ipcomb]]
                    ratioObj = glObj[:,1]/glObj[:,0]  #amore/aless
                    minimise_gate_cnstr.append(ratioObj >= 1)
                    #print(f"Debug: glitchOptObj(): mincnstr: {ratioObj}>=1 for gate {n}")

                    #glitch minimisation Objective from previous
                    Obj = pow(ratioObj,glitchExponent)
                    print("Min Obj=",Obj)
                    numberofminobj = numberofminobj + 1
                    minimise_objective = minimise_objective + sum(Obj)
                    #print(minimise_objective)             
                    #print(f"Debug: glitchOptObj(): min {numberofminobj} obj is {sum(Obj)} for gate {n}")
 
 
            else: #if gate has no or 1 nonPI inputs
                if critical[n,0] and Glog[n] != 1:
                    #print(f'Debug: glitchOptObj(): {n} is under glitch maximisation but has only one input ')
                    maximise_criticalgates.append(n)
                    criticalGateswithPI.append(n)
                    Gsize_critical_withprimary = Gsize_critical_withprimary + Gsize[n]
                    if len(Iparr[n]) != Ips[n] and len(Iparr[n]) == 1 and Glog[n] != 1 : #gatewith one non-PI & atleast one PI atkr added
                        #breakpoint()
                        modifiedGates.append(Iparr[n][0])
                        maximise_gate_cnstr.append(Tarr[Iparr[n][0]] >= Tinparr+inertial_delay_frac * inertialdelay_GM[n]) 


        else :                      #Primary inputs
            gate_cnstr.append(Tarr[n] >= Tinparr + Fout[n] + parasiticDelay[n])
            primary_gates.append(n)
            #if critical[n,1]:
            #    minimise_objective = minimise_objective + (Tarr[n] ** glitchExponent)
            #    numberofminobj = numberofminobj + 1

        '''
        #Sizing contraints
        if n == 29: # SBOX_272
            gate_cnstr.append(Gsize[n] <= 10)
            gate_cnstr.append(Gsize[n] >= 1)
        elif n == 103: # SBOX_274
            gate_cnstr.append(Gsize[n] <= 1.1)
            gate_cnstr.append(Gsize[n] >= 1)
        #elif n == 25: # SBOX_275
        #   gate_cnstr.append(Gsize[n] >= 1.5)
        #    gate_cnstr.append(Gsize[n] <= maxGsize)
        else:
            gate_cnstr.append(Gsize[n] <= maxGsize)
            gate_cnstr.append(Gsize[n] >= 1)
        #gate_cnstr.append(Gsize[n] <= 1.5*AMsol["variables"]["x"][n])
        '''
        if(parasiticDelay[n]>10):
            gate_cnstr.append(Gsize[n] <= 10)
            gate_cnstr.append(Gsize[n] >= 1)
        else:
            gate_cnstr.append(Gsize[n] <= maxGsize)
            gate_cnstr.append(Gsize[n] >= 1)

    # breakpoint()
    #gate_cnstr.append(Gsize[37]<=6)
    #maximise_gate_cnstr.append(Gsize_noncritical <= excessP*AMGsize_noncritical)
    maximise_gate_cnstr.append(Gsize_noncritical <= (excessP)*AMGsize_noncritical)
    #gate_cnstr.append(Gsize.sum() <= excessP*gsPower)
    area_objective = Gsize_noncritical + Gsize_critical_withprimary  # atkr added


    # minmax obhective and constraints
    constraints = gate_cnstr + minimise_gate_cnstr + maximise_gate_cnstr
    constraints = constraints + [Ts <= Twall*T0+Tinparr]  # atkr modified

    print(f"Debug: glitchOptObj(): minimise_objective is {minimise_objective}")
    print(f"Debug: glitchOptObj(): maximise_objective is {maximise_objective}")
    noObjective = 0
    if numberofmaxobj == 0 and numberofminobj ==0:
        noObjective = 1
    numberofmaxobj = 1 if numberofmaxobj == 0 else numberofmaxobj
    numberofminobj = 1 if numberofminobj == 0 else numberofminobj
    objective_picker = 1


    if objective_picker == 0:
        objective = minimise_objective/numberofminobj
        print(f'Info: glitchOptObj(): Picked only minimise objective')
    elif objective_picker == 1:
        objective = (minimise_objective/numberofminobj) +(maximise_objective/numberofmaxobj)
        print(f'Info: glitchMinMaxObj(): Picked normalised minimise and maximise objective')
    elif objective_picker == 2:
        coeffi_2 = Variable("coeffi_2")
        coeffi_1 = Variable("coeffi_1")
        gate_cnstr.append(coeffi_1*coeffi_2 <= 1)
        gate_cnstr.append(coeffi_2<=0.5)
        objective = coeffi_1*(minimise_objective/numberofminobj) +coeffi_2*(Ts/T0)
        print(f'Info: glitchMinMaxObj(): Picked normalised minimise and maximise objective')
    else:
        objective = Ts
        print(f'Info: glitchMinMaxObj(): Picked timing objective')
    objective = Ts if noObjective else objective 
    #print("\n\nConstraints\n\n",constraints)
    print(f"Info: glitchOptObj(): objective is {objective}")
    m = Model(objective, constraints)           #Use solver
    #from gpkit.constraints.relax import ConstraintsRelaxedEqually
    #allrelaxed = ConstraintsRelaxedEqually(m0)
    #m = Model(allrelaxed.relaxvar, allrelaxed)
    
    try :
        sol = m.solve(verbosity = 2)
        print(f'Info: glitchMaxObj(): Number Of Critical gates {critical.sum()} out of {N} of which {len(modifiedGates)} are modified')
        print(f'Info: glitchMaxObj(): fracxTwall allowed is {Twall_i*T0} and Glitchmin obtained is {sol["variables"]["Ts"]}')
        primary_gates_GM_sizes = sol["variables"]["x"][primary_gates]
        print("\n\n")
        #num_constraints = len(m.program.constraints)
        #print(f"Debug: Total number of constraints created by the GM solver: {num_constraints}")
        #print(sol["variables"].get("a", None))
        return True,sol,primary_gates_GM_sizes,modifiedGates,minimise_criticalgates,maximise_criticalgates,criticalGateswithPI
        #return True,sol,primary_gates_GM_sizes,modifiedGates,minimise_criticalgates,maximise_criticalgates,primary_gates
    
    except (exceptions.DualInfeasible) :
        print("exceptions.DualInfeasible")
        return False,None,None,None,None,None,None
    except (exceptions.Infeasible) :
    	print("Model is infeasible. Details:")
    	print(e)  # Print the exception message for more information
    	m.debug()  # C
    	return False,None,None,None,None,None,None
    except (exceptions.InvalidGPConstraint) :
        print("exceptions.InvalidGPConstraint")
        return False,None,None,None,None,None,None
    except (exceptions.InvalidLicense) :
        print("exceptions.InvalidLicense")
        return False,None,None,None,None,None,None
    except (exceptions.InvalidPosynomial) :
        print("exceptions.InvalidPosynomial")
        return False,None,None,None,None,None,None
    except (exceptions.InvalidSGPConstraint) :
        print("exceptions.InvalidSGPConstraint")
        return False,None,None,None,None,None,None
    except (exceptions.PrimalInfeasible) :
        print("exceptions.PrimalInfeasible")
        return False,None,None,None,None,None,None
    except (exceptions.UnboundedGP) :
        print("exceptions.UnboundedGP")
        return False,None,None,None,None,None,None
    except (exceptions.UnknownInfeasible) :
        print("exceptions.UnknownInfeasible")
        return False,None,None,None,None,None,None
    except (exceptions.UnnecessarySGP) :
        print("exceptions.UnnecessarySGP")
        return False,None,None,None,None,None,None
    except(RuntimeWarning,ValueError):
        print("Error")
        return False,None,None,None,None,None,None
    

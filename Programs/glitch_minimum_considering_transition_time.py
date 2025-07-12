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

                                    #Glitch minimization
def glminReducedObj_considering_transition_time(AMsol,N,T0,F,Opsize,Glog,Iparr,indIparr,Ips,maxIp,gsPower,GSarrT,parasiticDelay,gate_output_wire_capacitance,Cref,input_depth,circuit_name,critical=None,excessP=1.05,glExp=2,x0=20,Twall=1.2) :
    '''
    I/p to function
    
    O/p of function
    '''
    cost_dict = {"c432": 1222982.0,"c880": 544093.5,"c1908": 131214.4,"c2670": 124713.6,"c3540": 1501226.0,"c5315":837555.0,"c6288":2212.771,"c7552":143618.8,"adder":1912.11,"sine":275630.0,"cavlc":6232.367,"i2c":241683.5}
    #"adder":7551.68,
    print("Enter Glitch Optmzn.")
    inertial_delay_fraction = 0
    #print("input_depth=",input_depth[68],input_depth[69])
    AM_sizes_sum = AMsol["variables"]["a"].sum()
    AM_sizes_sum_of_squares = np.sum(AMsol["variables"]["a"]**2)
                                    #Dynamic default
    # if critical is None :
    # critical = np.ones(N)
                                    #Declare Variablesconstraints = constraints + [Ts <= 1.1*T0]
    Gsize = VectorVariable(N,"x")   #Gate sizes
    Tarr = VectorVariable(N,"a")    #Arrival times
    Ts = Variable("Ts")             #Timing wall (used in TIMING MIN)
    #alpha = Variable("alpha")
    #beta = Variable("beta")
    #time_objective = Variable("time_obj")
    #area_objective = Variable("area_obj") 
    X = diag(1/Gsize)               #Matrix used for computation
    primary_gates = []
    eta = 0.21
#    parasiticDelay = np.ones(N)    #Delay caused by parasitic capacitance
    
                                    #Computations from initial data
#    Fout = (F@ Gsize + Glog*(gate_output_wire_capacitance/Cref) + Glog*Opsize)@ X  #Fan out matrix (with o/p Cap)
    Fout = (F@ Gsize + (gate_output_wire_capacitance/Cref) + Opsize)@ X 
#    Fout = (F@ Gsize + Glog*Opsize)@ X 
    arrind = np.where(F!=0)             #Indices with non-zero 
    Iparr = array([arrind[0][np.where(arrind[1] == i)] for i in range(0,N)])    #Arrival time matrix    
                                    #Objective
    objective = 0
    toprint,toprint2 = 0,0
    a1,a2 = 0,0
    Fout_with_parasitic_delay = np.zeros(shape=(N),dtype=object)
    
    for n in range(N):
        Fout_with_parasitic_delay[n] = Fout[n] + parasiticDelay[n]
                                    #Equation writing
    gate_cnstr = []
    for n in range(0,N) :
                                    #Evaluate parasitic delay
        if Glog[n] != 1 :
            if Ips[n] == 1:
                print("Something is wrong")
            else :
                pass
 #               parasiticDelay[n] = Ips[n]*(Ips[n]+5)/6
    
        if Opsize[n] != 0 :         #For primary o/p constraint
            gate_cnstr.append(Tarr[n] <= Ts)
            
        if len(Iparr[n])!=0 :       #Arrival time contraints
            for i in range(0,len(Iparr[n])) :
                gate_cnstr.append(Tarr[n] >= Fout_with_parasitic_delay[n] + eta * Fout_with_parasitic_delay[Iparr[n][i]] + Tarr[Iparr[n][i]])
                # gate_cnstr.append(Tarr[n] >= Fout[n] + parasiticDelay[n] + Tarr[Iparr[n][i]])
                # gate_cnstr.append(Tarr[n] >= Fout[n] + Tarr[Iparr[n][i]])                
            
                                    #Minimize arrival times of gates w/ primary inputs
            if len(Iparr[n]) != Ips[n] and Glog[n] != 1 :
                # if critical[n] != 0 :
                #     a2+=1
                # pass
                for i in range(0,len(Iparr[n])) :
                    #print(input_depth[n])
                    if max(input_depth[n]) <= 100 :
                        if 0 in input_depth[n] :
                            #print("TRUE")
                            pass
                        #if(max(input_depth[n]) < 3):
                            
                        #print(max(input_depth[n]))
                        #print("n and i",n,i,Tarr[Iparr[n][i]])    
                        objective = objective + critical[n]*(Tarr[Iparr[n][i]]**glExp)#*(Gsize[n])
                        #objective = objective + critical[n]*((Tarr[Iparr[n][i]]/parasiticDelay[n])**glExp)    
                        #pass
                    toprint = toprint + critical[n]*(GSarrT[Iparr[n][i]]**glExp)
                    if critical[n]!=0:
                        a1 += 1
                    # pass

            if len(Iparr[n]) >= 2 :
                                    #Threshold for 2+ i/ps
                arrThres = ceil(len(Iparr[n])/2)
                #print("thres",arrThres,"len",len(Iparr[n]))
                if arrThres >= 2 :  #Take those which have more than 3 inputs
                    inputset = np.argsort(GSarrT[Iparr[n]])
                    arrTset = list(inputset)[:int(floor(arrThres/2))] + list(inputset)[-int(ceil(arrThres/2)):]
                else :              #For 2 input gates
                    arrTset = range(len(Iparr[n]))
                    inputset = range(len(Iparr[n]))

                #print(n,"arr",arrTset)
                #print("ip",inputset)
                temp = combinations(arrTset,2)
                ipcomb = array(list(temp))
                                    #Array of size matching the ipcomb and of same gate(n)
                nArr = n*np.ones(shape(ipcomb)).astype(int)
                                    #Glitch objective as ratio of array
                glObj = Tarr[indIparr[nArr,ipcomb]]
                ratioObj = glObj[:,1]/glObj[:,0]
                Obj = critical[n]*pow(ratioObj,glExp)
                                    #Print GS arrival time ratios to compare
                # print(n)
                tocompare = GSarrT[indIparr[nArr,ipcomb]]
                tocompare = tocompare[:,1]/tocompare[:,0]
                totemp = critical[n]*pow(tocompare,glExp)

                # tocompare2 = newvar[indIparr[nArr,ipcomb]]
                # tocompare2 = tocompare2[:,1]/tocompare2[:,0]
                # totemp2 = critical[n]*pow(tocompare2,glExp)

                # if critical[n]!=0:
                #         a2 += 1
                #print(sum(Obj))
                # objective = objective + sum(Obj)*(Gsize[n])
                objective = objective + sum(Obj)
                # # print(sum(totemp),sum(totemp2))
                toprint = toprint + sum(totemp)
                # toprint2 = toprint2 + sum(totemp2)
                # print(n,n)
                
                #if ratioObj.any() != 0 and critical[n] != 0:
                #if glObj.any() != 0 :
                    #gate_cnstr.append(Fout[n]/glObj[:,1] + glObj[:,0]/glObj[:,1] <= 1)
                if (critical[n] != 0):
                    ratioObj = critical[n] * (glObj[:,0]  + inertial_delay_fraction * (Fout[n] + parasiticDelay[n]))/(critical[n] * glObj[:,1])

                if ratioObj.any() != 0 and critical[n] != 0:
                # #if glObj.any() != 0 :
                    gate_cnstr.append(ratioObj <= 1)

        else :                      #Primary inputs
            gate_cnstr.append(Tarr[n] >= Fout[n] + parasiticDelay[n])
            #sizing constraint for primary gates
            primary_gates.append(n) 
            gate_cnstr.append(Gsize[n] <= 20)
            # gate_cnstr.append(Tarr[n] >= Fout[n])
                                    #Sizing contraints
        #gate_cnstr.append(Gsize[n] <= GSsizes[n])

        gate_cnstr.append(Gsize[n] >= 1)
        gate_cnstr.append(Gsize[n] <= x0)
    #gate_cnstr.append(alpha * beta <= 20)
    #gate_cnstr.append(alpha >= 1)
    #gate_cnstr.append(alpha >= 0.01)
    #gate_cnstr.append(beta >= 0.01)
    #gate_cnstr.append(alpha > 0)
    #gate_cnstr.append(beta >= 1)
    #gate_cnstr.append(beta > 0)
    #time_objective = objective/cost_dict[circuit_name]
    #area_objective = (Gsize.sum())**2 / AM_sizes_sum
    
    gate_cnstr.append(Gsize.sum() <= excessP*gsPower)

    
    # print(objective)
    constraints = gate_cnstr
    constraints = constraints + [Ts == Twall*T0]  #Add timing spec
    #area_square_trial = np.square(Gsize)
    #area_squared = 0
    #for i in range(len(Gsize)):
    #    area_squared = area_squared + Gsize[i]**2
    #objective = 0.9 *(1/alpha) * objective/cost_dict[circuit_name] + 0.1 * (1/beta) * (Gsize.sum()) / AM_sizes_sum
    #objective = 0.9 * objective/cost_dict[circuit_name] + 0.1 * Gsize.sum()/ AM_sizes_sum 
    #objective_terms = objective.split('+')
    #objective = 0.9 * objective + 0.1 * Gsize.sum()
    #print("area_squared=",area_squared)
    
    m = Model(objective, constraints)           #Use solver
    #for i in range(N):
    #    print(i,critical[i])

    #sol = m.debug()
    #sol = m.solve()
    #sol = m.solve(verbosity = 1)
    # print("Objective function for GM",objective)
    #return sol
#    print("GM constraints = ",constraints)
#    if(objective == 0):
#        objective = Gsize.sum()
#        gate_cnstr.append(Gsize.sum() <= gsPower)
#    else:
#        gate_cnstr.append(Gsize.sum() <= excessP*gsPower)
    #objective = 0
    #print("GM objective = ",objective)
    try :
        sol = m.solve(verbosity = 2)
        #print("alpha = ",sol["variables"]["alpha"])
        #print("beta =",sol["variables"]["beta"])
        #print("time_objective =",sol["variables"]["time_obj"])
        #print("area_objective=",sol["variables"]["area_obj"])
        #print("time_objective=",sol["variables"]["time_obj"])
        #print(sol["cost"])
###        print(sol["cost"])
###        print(toprint)
###        print(a2)
###        print(len(np.where(critical==1)[0]))
        # print(toprint2)
        # print(a1,a2)
        #print(sum(sol["variables"]["x"]))
        #print("GM arrival times =",sol["variables"]["a"])
        #print("1.1T0, Ts",1.1*T0,sol["variables"]["Ts"])
        primary_gates_GM_sizes = sol["variables"]["x"][primary_gates]
        objective = 0
        for n in range(0,N) :
            if len(Iparr[n])!=0 :       #Arrival time contraints             
                
                                        #Minimize arrival times of gates w/ primary inputs
                if len(Iparr[n]) != Ips[n] and Glog[n] != 1 :
                    # if critical[n] != 0 :
                    #     a2+=1
                    # pass
                    for i in range(0,len(Iparr[n])) :
                        #print(input_depth[n])
                        if max(input_depth[n]) <= 100 :
                            if 0 in input_depth[n] :
                                #print("TRUE")
                                pass
                            #if(max(input_depth[n]) < 3):
                                
                            #print(max(input_depth[n]))
                            #print("n and i",n,i,Tarr[Iparr[n][i]])    
                            objective = objective + critical[n]*(sol["variables"]["a"][Iparr[n][i]]**glExp)#*(Gsize[n])
                            #objective = objective + critical[n]*((Tarr[Iparr[n][i]]/parasiticDelay[n])**glExp)    
                            #pass
                        toprint = toprint + critical[n]*(GSarrT[Iparr[n][i]]**glExp)
                        if critical[n]!=0:
                            a1 += 1
                        # pass

                if len(Iparr[n]) >= 2 :
                                        #Threshold for 2+ i/ps
                    arrThres = ceil(len(Iparr[n])/2)
                    #print("thres",arrThres,"len",len(Iparr[n]))
                    if arrThres >= 2 :  #Take those which have more than 3 inputs
                        inputset = np.argsort(GSarrT[Iparr[n]])
                        arrTset = list(inputset)[:int(floor(arrThres/2))] + list(inputset)[-int(ceil(arrThres/2)):]
                    else :              #For 2 input gates
                        arrTset = range(len(Iparr[n]))
                        inputset = range(len(Iparr[n]))

                    #print(n,"arr",arrTset)
                    #print("ip",inputset)
                    temp = combinations(arrTset,2)
                    ipcomb = array(list(temp))
                                        #Array of size matching the ipcomb and of same gate(n)
                    nArr = n*np.ones(shape(ipcomb)).astype(int)
                                        #Glitch objective as ratio of array
                    glObj = sol["variables"]["a"][indIparr[nArr,ipcomb]]
                    ratioObj = glObj[:,1]/glObj[:,0]
                    Obj = critical[n]*pow(ratioObj,glExp)
                                        #Print GS arrival time ratios to compare
                    # print(n)
                    tocompare = GSarrT[indIparr[nArr,ipcomb]]
                    tocompare = tocompare[:,1]/tocompare[:,0]
                    totemp = critical[n]*pow(tocompare,glExp)
                    objective = objective + sum(Obj)
                    toprint = toprint + sum(totemp)
        print("objective_time_cost=",objective)
        area_check = sol["variables"]["x"].sum()
        print("objective_area_cost=",area_check)
        #print("check =",0.9*(objective)/cost_dict[circuit_name] + 0.1*(area_check / AM_sizes_sum))


        
        return sol,primary_gates_GM_sizes

    except (exceptions.DualInfeasible) :
        print("exceptions.DualInfeasible")
        return None
    except (exceptions.Infeasible) :
        print("exceptions.Infeasible")
        return None
    except (exceptions.InvalidGPConstraint) :
        print("exceptions.InvalidGPConstraint")
        return None
    except (exceptions.InvalidLicense) :
        print("exceptions.InvalidLicense")
        return None
    except (exceptions.InvalidPosynomial) :
        print("exceptions.InvalidPosynomial")
        return None
    except (exceptions.InvalidSGPConstraint) :
        print("exceptions.InvalidSGPConstraint")
        return None
    except (exceptions.PrimalInfeasible) :
        print("exceptions.PrimalInfeasible")
        return None
    except (exceptions.UnboundedGP) :
        print("exceptions.UnboundedGP")
        return None
    except (exceptions.UnknownInfeasible) :
        print("exceptions.UnknownInfeasible")
        return None
    except (exceptions.UnnecessarySGP) :
        print("exceptions.UnnecessarySGP")
        return None
    except(RuntimeWarning,ValueError):
        print("Error")
        return None
    

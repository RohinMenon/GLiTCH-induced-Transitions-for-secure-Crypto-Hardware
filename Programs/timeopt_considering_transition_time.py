                                    #Import libraries
from pylab import *
from gpkit import VectorVariable, Variable, Model, units
from gpkit.constraints.bounded import Bounded
from itertools import *
import random
from pickle import dump             #!pip install pickle-mixin :to install pickle
from pickle import load
import csv
import sys
import time
from pyparamopt import *
sys.setrecursionlimit(16000)

                                    #Timing Minimization
def timeopt_considering_transition_time(N,F,Opsize,Glog,Iparr,Ips,maxIp,parasiticDelay,gate_output_wire_capacitance,Cref,x0=20) :
    '''
    I/p to function
    F : matrix which consists of logical effort values at connections
    Opsize : Vector with output capacitance values (primary outputs)
    Glog : Vector with logical effort values of gates
    Iparr : Contains indices of gate outputs connected to input of each gate
    
    O/p of  function
    T0 : Timing wall with upper bound on sizes
    indIparr : input indices as an array
    '''
    print("Info: timeopt_considering_transition_time(): Enter Timing Optmzn.")
                                        #Declare Variables
    Gsize = VectorVariable(N,"x")       #Gate sizes
    Tarr = VectorVariable(N,"a")        #Arrival times
    Ts = Variable("Ts")                 #Timing wall (used in TIMING MIN)
    X = diag(1/Gsize)                   #Matrix used for computation
    indIparr = (-1)*np.ones((N,maxIp))  #Ip arrival time indices
    eta = 0.21
#    parasiticDelay = np.ones(N)    #Delay caused by parasitic capacitance
    
                                    #Computations from initial data
#    Fout = (F@ Gsize +  Glog*Opsize)@ X
#    Fout = (F@ Gsize + Glog*(gate_output_wire_capacitance/Cref) +  Glog*Opsize)@ X  #Fan out matrix (with o/p Cap)
    Fout = (F@ Gsize + (gate_output_wire_capacitance/Cref) + Opsize)@ X 
    arrind = np.where(F!=0)             #Indices with non-zero 
    Iparr = array([arrind[0][np.where(arrind[1] == i)] for i in range(0,N)])#Arrival time matrix
    ####print("Arrind=",arrind)
    ####print("Iparr=", Iparr)
                                    #Objective
    objective = Ts
    
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
#                parasiticDelay[n] = Ips[n]*(Ips[n]+5)/6
        
        if Opsize[n] != 0 :         #For primary o/p constraint
            gate_cnstr.append(Tarr[n] <= Ts)
        
        if len(Iparr[n])!=0 :       #Arrival time contraints
            for i in range(0,len(Iparr[n])) :
                gate_cnstr.append(Tarr[n] >= Fout_with_parasitic_delay[n] + eta * Fout_with_parasitic_delay[Iparr[n][i]] + Tarr[Iparr[n][i]])
                #gate_cnstr.append(Tarr[n] >= Fout[n] + parasiticDelay[n] + Tarr[Iparr[n][i]])      
        
        else :                      #Primary inputs
            gate_cnstr.append(Tarr[n] >= Fout[n] + parasiticDelay[n])
                                    #Sizing contraints
        gate_cnstr.append(Gsize[n] >= 1)
        gate_cnstr.append(Gsize[n] <= x0)
                                    #Add arr time indices to array
        indIparr[n][:len(Iparr[n])] = array(Iparr[n])

    constraints = gate_cnstr        
    m = Model(objective, constraints)   #Using solver
    #m.debug()
    sol = m.solve(verbosity = 0)
    T0 = sol["variables"]["Ts"]
    #print(sol["variables"]["x"])
    indIparr = indIparr.astype(int)
        
    return T0,indIparr



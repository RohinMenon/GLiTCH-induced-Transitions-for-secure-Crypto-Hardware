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
sys.setrecursionlimit(16000)

                                   #Area minimization
def gatesize_considering_transition_time(N,T0,F,Opsize,Glog,Iparr,indIparr,Ips,maxIp,parasiticDelay,gate_output_wire_capacitance,Cref,x0=20,Twall=1.2) :
    '''
    I/p to function
    
    O/p of function
    '''
    print("Enter Sizing Optmzn.")
                                        #Declare Variables
    Gsize = VectorVariable(N,"x")       #Gate sizes
    Tarr = VectorVariable(N,"a")        #Arrival times
    Ts = Variable("Ts")                 #Timing wall (used in TIMING MIN)
    X = diag(1/Gsize)                   #Matrix used for computation
    primary_gates = []
    eta = 0.21
#    parasiticDelay = np.ones(N)     #Delay caused by parasitic capacitance
                                       
                                    #Computations from initial data
    #Fout = (F@ Gsize + Glog*(gate_output_wire_capacitance/Cref) + Glog*Opsize)@ X  #Fan out matrix (with o/p Cap)
    Fout = (F@ Gsize + (gate_output_wire_capacitance/Cref) + Opsize)@ X 
#    Fout = (F@ Gsize + Glog*Opsize)@ X
    arrind = np.where(F!=0)             #Indices with non-zero 
    Iparr = array([arrind[0][np.where(arrind[1] == i)] for i in range(0,N)])    #Arrival time matrix
                                    #Objective
    print("N = ",N)
    objective = Gsize.sum()

    Fout_with_parasitic_delay = np.zeros(shape=(N),dtype=object)
    
    for n in range(N):
        Fout_with_parasitic_delay[n] = Fout[n] + parasiticDelay[n]
        
    #print(objective)
#    objective = 0
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
                #gate_cnstr.append(Tarr[n] >= Fout[n] + parasiticDelay[n] + Tarr[Iparr[n][i]]) 
                     
        else :                      #Primary inputs
            gate_cnstr.append(Tarr[n] >= Fout[n] + parasiticDelay[n])
                                    #Sizing contraints
        if len(Iparr[n]) == 0:
            primary_gates.append(n)
        #    gate_cnstr.append(Gsize[n] <= 8)
        
        gate_cnstr.append(Gsize[n] >= 1)
        gate_cnstr.append(Gsize[n] <= x0)

    constraints = gate_cnstr
    #print(objective)
    constraints = constraints + [Ts == Twall*T0]  #Add timing spec
    #print("AM constraints = ",constraints)
    m = Model(objective, constraints)           #Use solver
    sol = m.solve(verbosity = 2)
    #print(sol["constraints"])
    #print("1.1T0, Ts",1.1*T0,sol["variables"]["Ts"])
    #print("AM sizes = ",sol["variables"]["x"])
    #print("AM Arrival times = ",sol["variables"]["a"])
    primary_gates_AM_sizes = sol["variables"]["x"][primary_gates]
    #print("AM sizes of primary gates = ",sol["variables"]["x"])
        
    return sol,primary_gates_AM_sizes

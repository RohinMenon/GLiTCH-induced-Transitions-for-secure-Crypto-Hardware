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
                                    #Import parser


def paramopt(F_in,Opsize_in,Glog_in,Ips_in,parasiticDelay_in,gate_output_wire_capacitance_in) :
    '''
    I/p to function
    psr : netlist info from parser
    
    O/p of function
    F : matrix which consists of logical effort values at connections
    Opsize : Vector with output capacitance values (primary outputs)
    Glog : Vector with logical effort values of gates
    Iparr : Contains indices of gate outputs connected to input of each gate
    '''
                                    #Import data from parser
    F = F_in                       #Fan out matrix
    Opsize = Opsize_in             #Output Capcitance values
    Glog = Glog_in  #Gate logical effort
    N = len(F)                      #No. of gates
    arrind = np.where(F!=0)         #Indices with non-zero 
                                    #Arrival time matrix (which are I/ps to gates)
    Iparr = array([arrind[0][np.where(arrind[1] == i)] for i in range(0,N)])
    #print(f'paramout():\nF={F}\narrind = {arrind}\nIparr = {Iparr}')  
    Ips = Ips_in  #No of inputs of each gate
    Ips = array(list(Ips))
    maxIp = max(Ips)                #Maximum no of inputs at any gate
    # criticality = psr.criticality
    parasiticDelay = parasiticDelay_in
    gate_output_wire_capacitance = gate_output_wire_capacitance_in
    
    return F,Opsize,Glog,N,Iparr,Ips,maxIp,parasiticDelay,gate_output_wire_capacitance

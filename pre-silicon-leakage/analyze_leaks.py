################################################################################
# Script: analyze_leaks.py
# Purpose: Perform side-channel leakage analysis using simulated VCD traces.
#
# Description:
#   This script analyzes the side-channel leakage of a hardware design based on
#   its simulation waveforms (VCDs). It correlates switching activity in the VCD
#   with known input values (e.g., plaintexts) to assess how much information
#   leaks through signal transitions.
#
# Requirements:
#   - VCD files named as 0.vcd, 1.vcd, ..., each corresponding to a simulation run
#   - A plaintext input file named `txtfile.txt`, containing the exact input used
#     in each simulation, one per line, in the same order as the VCD files
#
# Usage:
#   python3 analyze_leaks.py <KEY> <RESULTS_FOLDER> -n <NUM_TRACES> -r <LEAKS_FOLDER> -p <NUM_THREADS>
#
# Arguments:
#   <KEY>             - The constant key used during simulation
#   <RESULTS_FOLDER>  - Prefix for output result files
#   -n <NUM_TRACES>   - Number of traces (i.e., number of VCDs and input lines)
#   -r <LEAKS_FOLDER> - Directory containing the VCDs and txtfile.txt
#   -p <NUM_THREADS>  - Number of threads to use for parallel processing
#
# Example:
#   python3 analyze_leaks.py 100 "FN_unmasked_aes_key_100" -n 256 -r sboxes/aes -p 32
#
# Output:
#   - Leakage metrics such as correlation scores or guessing entropy
#   - Processed results stored in the specified <RESULTS_FOLDER>
################################################################################


import argparse
import math
import numpy as np
import operator
import os
import pickle as pk
import re
import subprocess
import sys
import time

from datetime import datetime
from itertools import combinations
from scipy.stats.stats import pearsonr
from tqdm import tqdm
from Verilog_VCD import Verilog_VCD as v
from multiprocessing import Pool

# Reads input values generated during simulation from 'txtfile.txt'
def loadData():
    a = []
    with open('txtfile.txt', 'r') as f:
        buff = f.read().split('\n')
    for d in buff[:-1]:
        a.append(d)
    a = np.array(a, dtype='uint64')
    return a

# Computes the oracle trace by XORing input trace and secret key
def computeOracle(k):
    ip1 = loadData()
    y = np.bitwise_xor(ip1, k)
    return y

################################################################################
################################################################################

# Global variables for file paths, signal tracking, and intermediate storage
vcdpath = 'vcd/'
filepath = 'pkl/'
pairs = []
sigArray1 = {}  # Stores the value carried by each signal for each run
sigGroup = {}
sigMatrix = {}
cipher = {}
O = {}
togglingSigs = set()

# Processes a subset of iterations in parallel: updates signal arrays, processes signals, computes leakage scores
def multiproc(num_iterations, rfiles, leaks_file_path, it):
    togglingSigs = set()
    for fn in range(1, num_iterations + 1):
        fname = str(fn)
        with open(filepath + rfiles[fn - 1], 'rb') as file:
            temp = pk.load(file)
            tempsigs = []
            tempvals = []
            try:
                tempsigs = temp[it][1][0]
                tempvals = temp[it][1][1]
            except:
                pass

            else:
                tempsigs = temp[it-1][1][0]
                tempvals = temp[it-1][1][1]
            togglingSigs.update(tempsigs)
            tempdict = updateSigArray(fname, tempsigs, tempvals)
    processSignals(togglingSigs, it)
    numSigs = computeAndSaveLeakageScores(leaks_file_path, num_iterations, key_value, togglingSigs, it)
    end_time = time.time()
    togglingSigs.clear()
    return numSigs

# Builds a dictionary mapping clock edges to signal names and their values
def createClkList(clkList, sname, tv):
    for x in tv:
        if x[0] not in clkList:
            clkList[x[0]] = [[], []]
            clkList[x[0]][0].append(sname)
            clkList[x[0]][1].append(x[1])
        else:
            clkList[x[0]][0].append(sname)
            clkList[x[0]][1].append(x[1])
    return clkList

# Reads VCD files, parses transitions, and stores the information in pickle files
def readVCD(num_iterations):
    print("----------- In Read VCD -------------")
    rng = range(num_iterations)
    for name, i in zip(['' + str(x) + '.vcd' for x in rng], rng):
        print("-----------Reading VCD-{} -------------".format(i))
        data = {}
        clockList = {}
        data = v.parse_vcd(vcdpath + name, use_stdout=0)
        for x in data:
            for index in range(len(data[x]['nets'])):
                signame = data[x]['nets'][index].get('hier') + '.' + data[x]['nets'][index].get('name')
                clockList = createClkList(clockList, signame, list(data[x]['tv']))
        with open(filepath + str(i) + '.pkl', 'wb') as f:
            pkdump = []
            for x in sorted(clockList):
                pkdump.append([x, clockList[x]])
            len_pkdump = len(pkdump)
            pk.dump(pkdump, f)
    print('Pickle files have been created successfully...')
    return len_pkdump

# Initializes the signal array dictionary for all runs, setting all signals to '0'
def initSigArray(rfiles):
    vcdname = '0.vcd'
    data = v.parse_vcd(vcdpath + vcdname, use_stdout=0)
    for f, n in zip(rfiles, range(1, len(rfiles) + 1)):
        fname = str(n)
        sigArray1[fname] = {}
        for s in data:
            sigArray1[fname][data[s]['nets'][0].get('hier') + '.' + data[s]['nets'][0].get('name')] = '0'
    with open('sigArray.pkl', 'wb') as f:
        for x in sigArray1:
            pk.dump([x, sigArray1[x]], f)
    print("SigArray has been created successfully")

# Orders strings alphanumerically for consistent sorting
def alphaNumOrder(string):
    return ''.join([format(int(x), '05d') if x.isdigit()
                    else x for x in re.split(r'(\d+)', string)])

# Initializes all unique pairs of iterations for Hamming distance calculation
def initpairs(num_iterations):
    return list(combinations(np.linspace(1, num_iterations, num_iterations).astype(int), 2))

# Loads the signal array dictionary from a pickle file
def loadSigArray():
    with open('sigArray.pkl', 'rb') as f:
        try:
            while True:
                temp = []
                temp = pk.load(f)
                sigArray1.update({temp[0]: temp[1]})
        except EOFError:
            pass

# Initializes global variables, loads signal arrays, and prepares the list of all signals
def init(num_iterations):
    global pairs, sigs
    loadSigArray()
    pairs = initpairs(num_iterations)
    sigs = [x for x in sigArray1['1']]

# Updates the signal array dictionary with new values for a specific run
def updateSigArray(k1, k2, v):
    tempdict = {}
    for k, v in zip(k2, v):
        sigArray1[k1][k] = v
        tempdict[k] = v
    return tempdict

# Computes Hamming distance between every pair of values for a given signal
def HammingDistanceSignalWise(sig):
    tempfile = {}
    cnt = 0
    for p in pairs:
        temp = []
        p1 = str(p[0])
        p2 = str(p[1])
        s1 = sigArray1[p1]
        s2 = sigArray1[p2]
        s1[sig] = s1[sig].replace('z', '0')
        s2[sig] = s2[sig].replace('z', '0')
        s1[sig] = s1[sig].replace('x', '0')
        s2[sig] = s2[sig].replace('x', '0')
        temp.append(bin(int(s1[sig], 2) ^ int(s2[sig], 2)).count('1'))
        tempfile[p] = int(np.sum(temp))
    return tempfile

# Processes a set of signals, computes Hamming distances, and stores the results in pickle files
def processSignals(sigs, it):
    for sig in tqdm(sigs, f"Processing signals {it}"):
        try:
            ham = (sig, HammingDistanceSignalWise(sig))
            temp = []
            for pair in pairs:
                temp.append(ham[1][pair])
            with open('modules/' + ham[0] + '.pkl', 'ab') as f:
                pk.dump(temp, f)
        except Exception as e:
            pass

# Loads and transposes data from pickle files for analysis
def transformData(signal):
    data = []
    file_path = 'modules/' + signal + '.pkl'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            try:
                while True:
                    data.append(pk.load(f))
            except EOFError:
                pass
    return np.transpose(data)

# Computes leakage scores (Pearson correlation) and saves results to a file
def computeAndSaveLeakageScores(leaks_file_path, num_iterations, key_value, togglingSigs, it):
    leaks = {}
    O = {}
    mx = {}
    O[1] = []
    init(num_iterations)
    y = computeOracle(key_value)
    for p in pairs:
        O[1].append(bin(y[p[0] - 1] ^ y[p[1] - 1]).count('1'))

    counter = 0
    counter1 = 0
    counter2 = 0
    zero_list = []
    for sig in togglingSigs:
        data = transformData(sig)
        zero_list.append(data.any())
        temp = []
        for sc in data.transpose():
            if len(O[1]) == len(sc):
                score = pearsonr(O[1], sc)[0]
                if math.isnan(score):
                    temp.append(0)
                    counter1 += 1
                else:
                    temp.append(np.abs(score))
                    counter2 += 1
            else:
                temp.append(0)
        leaks[sig] = temp
        counter += 1
    for m in leaks:
        mx[m] = max(leaks[m], default=0)
    leaks_x = []
    leaks_y = []
    sorted_sigwise = dict(sorted(mx.items(), key=operator.itemgetter(1), reverse=True))
    for x in sorted(mx):
        leaks_x.append(x)
        leaks_y.append(mx[x])
    with open(leaks_file_path + f"leaks{it}" + ".txt", "w") as f:
        f.write("Signal,Leakage\n")
        for x in sorted_sigwise:
            f.write("%s,%.4f\n" % (x, sorted_sigwise[x]))
        f.write("\n")
    return len(sorted_sigwise)

# Main function: runs the full analysis pipeline, manages multiprocessing, and saves results
def main(num_iterations, key_value, leaks_file_path, time_file_path, proc):
    start_time = time.time()
    print("----------- In Main -------------\n")
    nc2 = ((num_iterations * (num_iterations - 1)) / 2)
    len_dump = readVCD(num_iterations)
    rfiles = os.listdir(filepath)
    rfiles.sort(key=alphaNumOrder)
    initSigArray(rfiles)
    debug = 0  # Debug flag (not used)
    init(num_iterations)
    signals = [x for x in sigGroup]
    for x in signals:
        sigMatrix[x] = []
        for y in range(len(sigGroup[x])):
            temp = []
            sigMatrix[x].append(temp)
    result = []
    inp_multiproc = []
    pool = Pool(processes=proc)
    for i in range(0, len_dump):
        inp_multiproc.append((num_iterations, rfiles, leaks_file_path, i))
    numSigs = pool.starmap(multiproc, inp_multiproc)
    end_time = time.time()
    print("\n-------- Completed! --------")
    with open(time_file_path, "w") as sf:
        sf.write("Number of signals: {}\n".format(numSigs))
        sf.write("Total time taken: {:.4f}s\n".format(end_time - start_time))

if __name__ == '__main__':
    # Parses command-line arguments for key value, design name, iterations, output path, and number of processes
    my_parser = argparse.ArgumentParser(description='Pre-silicon power side-channel analysis using PLAN')
    my_parser.add_argument('KeyValue',
                           metavar='key_value',
                           type=int,
                           help='secret value in input Verilog file')
    my_parser.add_argument('Design',
                           metavar='design',
                           type=str,
                           help='name of the design being analysed')
    my_parser.add_argument('-n',
                           '--num-iterations',
                           type=int,
                           action='store',
                           help='number of iterations in behavioral simulation, default value = 1000')
    my_parser.add_argument('-r',
                           '--results-path',
                           type=str,
                           action='store',
                           help='name of directory within results/ directory to store results, default value = current timestamp')
    my_parser.add_argument('-p',
                           '--process',
                           type=int,
                           action='store',
                           help='no of cores that needs to be used')
    args = my_parser.parse_args()
    key_value = args.KeyValue

    design = args.Design
    proc = args.process
    if not proc:
        proc = os.cpu_count()
    num_iterations = args.num_iterations
    if not num_iterations:
        num_iterations = 1000
    results_path = args.results_path
    if results_path:
        results_path = 'results/' + results_path + '/' + design + '/'
    else:
        results_path = 'results/' + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + '/' + design + '/'
    if not os.path.isdir(results_path):
        os.makedirs(results_path)
    leaks_file_path = results_path + "leaks.txt"
    time_file_path = results_path + "time.txt"
    if not os.path.isdir('vcd/'):
        os.makedirs('vcd/')
    if not os.path.isdir('pkl/'):
        os.makedirs('pkl/')
    if not os.path.isdir('modules/'):
        os.makedirs('modules/')
    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    main(num_iterations, key_value, leaks_file_path, time_file_path, proc)

import sys
from timeBasedGlitchAnalysis import getGenerationPropagationCount
from read_inputs import *


def get_glitch(mname,clockPeriod,filePath):
    #filePath = "./"
    libName = "faraday"
    mode = "comb"

    numOfVectors = 1000

    vcdFilePath = filePath+mname+"_sdf_avg.vcd"
    sdfFile = filePath+mname+"_avg.sdf"#'inputs'+"/"+
    netlistPath = filePath+mname+"_netlist.v"#"inputs"+"/"+
    tmpFile = filePath+mname+"_tmp"#"inputs/"+

    gate_delays = storeGateDelay(mname, sdfFile)
    ckt_graph = build_graph(mode,tmpFile)
    drivenNets = getDrivenNets(ckt_graph)
    sym_netname = storeSignalSymbolMap(vcdFilePath,mname)

    glitchcount= getGenerationPropagationCount(mode, vcdFilePath, sym_netname, clockPeriod, 
            ckt_graph, gate_delays, drivenNets, numOfVectors)

    ##for key in glitchcount.keys():
    ##    print(key,":",glitchcount[key]['GeneratedGlitches'])
    ##print(glitchcount)

    return glitchcount


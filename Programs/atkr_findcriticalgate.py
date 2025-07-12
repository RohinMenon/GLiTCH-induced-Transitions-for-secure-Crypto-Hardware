def analyse_critical(leakscore_notiming,leakscore_AM,glitch_AM,Iparr,gate_type_list,gate_name,noOfGatesToConstraint):
    delta_leakscore = [round(a - b,4) for a, b in zip(leakscore_notiming, leakscore_AM)]
    #print(delta_leakscore)
    gate_position = [i for i in range(0,len(glitch_AM))] #TODO fix
    #gate_position = [i for i in range(0,gate_length)]
    tupled = sorted(zip(delta_leakscore,gate_position,gate_type_list,gate_name,leakscore_AM)) #positive score has been reduced with increase in glitch
    #print(tupled)
    tupled_AM = sorted(zip(leakscore_AM,delta_leakscore,gate_position,gate_type_list,gate_name),reverse=True) #positive score has been reduced with increase in glitch
    #print(tupled_AM)
    AMthreshold_MIN = 0.04
    AMthreshold_MAX = 0.03
    minGlitch_gates = []
    maxGlitch_gates = []
    minForce = []
    maxForce = []
    max_depend = [] 
    min_remove = []
    max_remove =[]
    #maxGlitch_gates = [t[1] for t in tupled if t[0] > 0 and t[2]!=NOT_1 and t[3]> AMthreshold_MAX ] 
    #minGlitch_gates = [t[1] for t in tupled if t[0] <= 0 and t[2]!=NOT_1 and t[3]> AMthreshold_MIN]


    ''' 
    mingatesconstraint = round(noOfGatesToConstraint)
    minGlitch_gates_NOT = [t for t in tupled if t[0] <=0][:mingatesconstraint]
    minGlitch_gates = [p[1] for p in minGlitch_gates_NOT if p[2]!='NOT1']
    minForce = [29] # 0.1297 highest leakage
    minForce = [29,68] # 0.1093 SBOX_275
    '''

    ''' 
    #Experiment recorded as 'Just MIN (2/3)N  without 0 deltaleak with min cnst'
    mingatesconstraint = round(noOfGatesToConstraint*(2/3))
    minGlitch_gates_list = [t for t in tupled if t[0]<0 and t[2]!='NOT1']
    minGlitch_gates = [p[1] for p in minGlitch_gates_list[:mingatesconstraint]]
    #minForce = [14,15,16,17,19,21,22,23,25,29,37,52,68,98,103,105,133,176,23,274,253,277] 

    maxgatesconstraint =  round(noOfGatesToConstraint*(1/3))
    maxGlitch_gates_list = [t for t in tupled if t[0]>0 and t[2]!='NOT1']
    #maxGlitch_gates = [p[1] for p in maxGlitch_gates_list[-maxgatesconstraint:]]
    '''
    
      
    #Expriment recorded as  'FIRST N GATES to MINIMISE OR MAXIMISE (min constraint)'
    tupled_AM_nonzero = [t for t in tupled_AM if t[1]!=0] 
    minGlitch_gates = [t[2] for t in tupled_AM_nonzero[:noOfGatesToConstraint] if t[1] < 0 and t[3]!="NOT1"]
    maxGlitch_gates = [t[2] for t in tupled_AM_nonzero[:noOfGatesToConstraint] if t[1] > 0 and t[3]!="NOT1"]
    
    minGlitch_gates_names = [t[4] for t in tupled_AM_nonzero[:noOfGatesToConstraint] if t[1] < 0 and t[3]!="NOT1"]
    maxGlitch_gates_names = [t[4] for t in tupled_AM_nonzero[:noOfGatesToConstraint] if t[1] > 0 and t[3]!="NOT1"]
    
    #print("min G gates", minGlitch_gates)
    #print("max G gates", maxGlitch_gates)
    #min_remove = [39,53,94] 
    #max_remove = [112,123,126]
    #maxForce = [116]
    #minForce = [23] 
    #minForce = [14,15,16,17,19,21,22,23]  #TODO:fix 
    #minForce = [120,122,129,87,130]
    #min_remove = [50,58,89,137,169,87,120,122,129,130]
    #maxForce = [164,153,169,27,50,145,165]
    #max_remove = [138,142,155,177,89,137,13,37,164,153,169,27,50,145,165]
    #min_remove = [87,120,122,129,58,130]
    #max_remove = [164,153,169,27,50,145,165, 138, 177, 142, 155, 137, 13, 37, 89]
    #max_remove = [5]
    #max_remove = [164,169,177]
    #max_remove = [88]
    #maxForce = [153]
    #max_remove =[13,138,142,177,164,169,27,50,145,165,27,50,145,164,165,169]
    #max_remove =[6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 18, 21, 23, 26, 27, 30, 31, 34, 35, 37, 38, 43, 44, 45, 46, 48, 49, 50, 52, 54, 55, 56, 57, 59, 60, 62, 64, 65, 66, 67, 69, 70, 71, 72, 73, 75, 78, 79, 80, 82, 83, 86, 
    #88, 89, 91, 95, 96, 97, 102, 111, 112, 113, 115, 119, 124, 126, 131, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 148, 151, 152, 153, 154, 155, 157, 158, 163, 164, 180, 165,166, 167, 169, 177]
    #min_remove = [32,41,87,101,122]
    #max_remove = [452, 434, 131, 323, 144, 439, 73, 328, 6, 473, 477, 388, 314]
    #min_remove = [378, 428, 324, 430, 485, 126, 420, 471, 452, 85, 459, 47, 345, 27, 395, 112, 21, 173, 334, 156, 381, 361, 202, 433]
    #maxForce = [99,284]
    #min_remove = [57, 60, 61, 43, 52, 3, 39, 56, 29, 46, 4, 33, 55, 53, 26, 2, 22, 14, 49, 13, 6, 35, 1, 38, 32, 7, 10, 30, 51, 28, 11, 42, 41, 5, 19] 

    '''
    maxgatesconstraint = round(noOfGatesToConstraint)
    maxGlitch_gates_list = [t for t in tupled if t[2]!='NOT1']
    maxGlitch_gates = [p[1] for p in maxGlitch_gates_list[:maxgatesconstraint]]
    '''

    for gateindex in maxForce:
        if gateindex not in maxGlitch_gates:
            maxGlitch_gates.append(gateindex)
        if gateindex in minGlitch_gates:
            minGlitch_gates.remove(gateindex)
    for gateindex in minForce:
        if gateindex not in minGlitch_gates:
            minGlitch_gates.append(gateindex)
        if gateindex in maxGlitch_gates:
            maxGlitch_gates.remove(gateindex)

    for element in maxGlitch_gates:
        inputs = Iparr[element]
        print("max element ", element)
        print("Inputs ",inputs)
        for i in range(len(inputs)): 
            gate = inputs[i]
            if gate not in max_depend:
                max_depend.append(gate)
       
    #print(f"Debug: findcriticalgate(): maxGlitchgates are {maxGlitch_gates}") 
    #print(f"Debug: findcriticalgate(): maxdependent are {max_depend}") 
    #print(f"Debug: findcriticalgate(): minGlitchgates are {minGlitch_gates}") 
    for element in minGlitch_gates:
        inputs = Iparr[element]
        print("min element ", element)
        print("Inputs ",inputs)
        for i in range(len(inputs)): 
            gate = inputs[i]
            if (gate in max_depend) or (gate in maxGlitch_gates):
                print(f"Warning: min constraints on {gate} due to {element} is affecting the existing max constraints")
                min_remove.append(element)

    for gate in min_remove:
        if gate in minGlitch_gates:
            minGlitch_gates.remove(gate)
    #delta_leakscore,gate_position,leakscore_notiming = map(list, zip(*tupled)) 
    for gate in max_remove:
    	if gate in maxGlitch_gates:
    		maxGlitch_gates.remove(gate)
    		
    print(maxGlitch_gates)
    print(maxGlitch_gates_names)
    print(minGlitch_gates)
    return maxGlitch_gates,minGlitch_gates


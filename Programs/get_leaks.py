def get_leaks(filepath,mname,leakfile):
    #leakfile = filepath+"/"+mname+"/"+mname+"_leaks.txt"
    netfile = filepath+"/"+mname+"/"+mname+"_genus.txt"

    try:
        lfile = open(leakfile,'r')
        nfile = open(netfile,'r')
        leakdatas = lfile.readlines()
        #print(leakdatas)
        netdatas = nfile.readlines()
        lfile.close()
        nfile.close()
    except IOError:
        print(f"Error: get_leaks(): Cant open {leakfile} or {netfile}")
        sys.exit(0)

    leakGraph = {}
    leaks = []

    for leakdata in leakdatas:
        leakdata = leakdata.strip()
        #print(leakdata)
        netname,leakprob = leakdata.split(',')
        leakGraph[netname] = leakprob
    
    for line in netdatas:
        line = line.strip()
        if (line.startswith('xor') or line.startswith('xnor') or line.startswith('not') or line.startswith('nand') or line.startswith('nor')):
            net = line.split('(')[1].split(',')[0]
            if(net in leakGraph):
                leaks.append((float)(leakGraph[net]))
                #print(f'net is {net} prob is {leakGraph[net]}')
            else:
                print(f'Warning: get_leaks(): {net} net is not present in leak_data. adding 2.00 by default')
                leaks.append((float)(2.00))
    #print(leaks)
    return leaks

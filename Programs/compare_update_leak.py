#!/usr/bin/python3
import os
import sys
import get_leaks

def updateLeakCsv(newleakdata,csvfile="metadata.csv",mname="SBOX",filepath="/home/ee18s050/cadence/digital_design/synthesis_4/circuit_files"):
    new_leak = get_leaks.get_leaks(filepath,mname,newleakdata)
    csvbasename = os.path.splitext(os.path.basename(csvfile))[0]
    csvdirname = os.path.dirname(csvfile)
    newcsvfile = os.path.join(csvdirname,csvbasename+"_updated.csv")


    try:
        oldcsvhandler = open(csvfile,'r')
        lines = oldcsvhandler.readlines()[1:]
        oldcsvhandler.close()
    except IOError:
        print(f"Cant open {csvfile}")
        sys.exit(0) 
   
    try:
        newcsvhandler = open(newcsvfile,'w')
        newcsvhandler.write("gate_name,gate_type,gate_number,gate_level,AMgate_size,GMgate_size,gate_time,notiming_leakscore,AM_leakscore,GM_leakscore,AMGM_delatascore,NOTAM_leakscore,to_minimize,to_maximize,is_PI,is_modified,AM_glitch_count,GM_glitch_count,delta_glitch_count\n")
        line_no = 0;
        for line in lines:
            line_list = line.split(',')
            line_list.insert(9,str(new_leak[line_no]))
            AmGmdelta_score = round(float(line_list[8])-float(line_list[9]),4)
            line_list.insert(10,str(AmGmdelta_score))
            NotAmdelta_score = round(float(line_list[7])-float(line_list[8]),4)
            line_list.insert(11,str(NotAmdelta_score))
            new_line = ','.join(line_list)
            newcsvhandler.write(str(new_line))
            line_no+=1
    except IOError:
        print(f"cant open {newcsvfile} to write")
        sys.exit()


if len(sys.argv) == 2:
    print(f'Info: Input leakdata passed as {sys.argv[1]}')
    updateLeakCsv(sys.argv[1])
elif len(sys.argv) == 3:
    print(f'Info: Input leakdata passed as {sys.argv[1]}')
    print(f'Info: Input csv file path passed as {sys.argv[2]}')
    updateLeakCsv(sys.argv[1],sys.argv[2])
elif len(sys.argv) == 4:
    print(f'Info: Input leakdata passed as {sys.argv[1]}')
    print(f'Info: Input csv file path passed as {sys.argv[2]}')
    print(f'Info: Input circuit name passed as {sys.argv[3]}')
    updateLeakCsv(sys.argv[1],sys.argv[1],sys.argv[3])
else:
    print(f"Error: Issue in {len(sys.argv)} Input arguments passed to the script.\nHelp: {sys.argv[0]} <newleakscore> <oldcsv> <circuitname>\naborting.....")


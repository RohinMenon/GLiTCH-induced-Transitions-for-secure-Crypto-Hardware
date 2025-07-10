#!/bin/bash

################################################################################
# Script: unmasked_aes_sbox.sh
# Purpose: Run simulations using Icarus Verilog (iverilog) to generate VCD traces
#          for side-channel analysis of unmasked AES S-Box designs.
#
# Usage:
#   ./unmasked_aes_sbox.sh <verilog_dir> <testbench_file> <num_iterations> <KEY>
#
#   Example:
#     ./unmasked_aes_sbox.sh verilog_files/Unmasked_Sbox_AES tb_unmasked_aes_sbox.v 100 42
#
# Arguments:
#   <verilog_dir>     - Directory containing Verilog source files
#   <testbench_file>  - Top-level testbench file inside <verilog_dir>
#   <num_iterations>  - Number of simulation runs to perform (e.g., 256)
#   <KEY>             - Key value (constant) to be used in the simulation
#
# Description:
#   - This script injects a sequence of values (e.g., plaintexts) and a fixed key
#     into the testbench using `define macros.
#   - It runs behavioral simulations with Icarus Verilog (iverilog + vvp) for
#     each iteration.
#   - The simulation produces a VCD (Value Change Dump) file per iteration.
#   - All VCDs are collected in the ./vcd/ directory.
#   - The plaintext values are saved to txtfile.txt for use as oracle data.
#   - After simulation, a Python-based leakage analysis is performed.
#   - Output results are processed and organized into a target output folder.
#   - Finally, temporary simulation files are cleaned up.
#
# Note:
#   - You can substitute Icarus Verilog with any other simulator, as long as
#     it generates compatible VCD files.
#   - You can also run a plaintext-only version by using the commented loop
#     at the bottom of this script.
################################################################################

inpdir="$1"
filename="$2"
# number of simulations to be performed
runs="$3"
key="$4"

# line numbers corresponding to initialization of the input variables
line1=1 # Pt (Plaintext)
lineK=2 # key

# line number corresponding to the dumpfile command
lineD=3 # dumpfile

# script to clean up temporary files created from previous simulation
./clean.sh

# Check if directories and files are provided
if [[ -z "$inpdir" || -z "$filename" || -z "$runs" ]]; then
  echo "Usage: $0 <input_dir> <verilog_filename> <num_runs>"
  exit 1
fi

# Check if input Verilog file exists
if [[ ! -f "$inpdir/$filename" ]]; then
  echo "File not found: $inpdir/$filename"
  exit 1
fi

# Create the output directory if it doesn't exist
mkdir -p ./vcd

for ((i = 0; i < runs; i++)); do
  # generating random values for each of the input variables
  # the maximum value possible for each variable must be updated below
  r1=$i  # $(od -N 8 -t uL -An /dev/random | tr -d " ")

  # plugging in the random values for PLAINTEXT in the Verilog file
  sed -i "${line1}s/.*/  	\`define PLAINTEXT $r1/" "$inpdir/$filename"

  # plugging in the predefined key in the Verilog file
  sed -i "${lineK}s/.*/  	\`define KEY $key/" "$inpdir/$filename"

  # plugging in the dumpfile name in the Verilog file
  sed -i "${lineD}s/.*/    \`define DUMPFILE \"$i.vcd\"/" "$inpdir/$filename"


  # running the behavioral simulation
  iverilog "$inpdir/"*.v -o "$inpdir/dumpfile" 
  vvp "$inpdir/dumpfile"

  # move the generated vcd file to the output folder
  mv "$i.vcd" ./vcd

  # storing the value of the variables required for oracle computation
  echo "$r1" >> txtfile.txt
done

echo "Simulation completed for $runs runs."
echo "VCDs generated for  $inpdir/$filename"


##### USE THIS TO GENERATE JUST THE PLAINTEXT FILE (txtfile.txt) FOR THE ABOVE
# ./clean.sh
# for ((i=0;i<=255;i++)); do
# echo "$i" >> txtfile.txt
# done
# echo "Txtfile.txt created successfully"

#######################################################################################################

python3 analyze_leaks.py 100 "FN_unmasked_aes_key_100" -n $runs -r sboxes/aes -p 32

# Process output
(cd output_processing/ && ./do_output.sh sboxes/aes/FN_unmasked_aes_key_100)

# Move output files
mkdir -p "output_processing/sboxes/aes"
mv "output_processing/FN_unmasked_aes_key_100"* "output_processing/sboxes/aes"

##### FINAL CLEAN
./clean.sh
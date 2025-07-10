#!/bin/bash

# Script to process multicycle simulations and compile results
folder="$(pwd)/../results/"
res=$1
res_folder="$folder""$res"
python3 readleaks.py $res_folder
python3 organize_leaks.py $res_folder
python3 processing_leaks.py $res_folder

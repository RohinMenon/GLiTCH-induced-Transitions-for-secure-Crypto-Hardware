#!/bin/bash

# Script to clean up temporary files created from previous simulation
echo "Cleaning temporary files created from previous simulations"
rm -rf vcd
rm -rf modules
rm -rf pkl
rm -rf txtfile*
rm -rf dumpfile
rm -rf sigArray.pkl

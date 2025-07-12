# GM-GP Code: Gate-level Optimization for Digital Circuits

This code implements geometric programming (GP) based optimization for digital circuit design, focusing on area minimization (AM) and glitch modification (GM) of gate-level circuits.

## Overview

The project performs timing-aware gate sizing optimization on digital circuits using geometric programming. It includes:

- **Area Minimization (AM)**: Optimizes gate sizes to minimize total circuit area while meeting timing constraints
- **Glitch Manipulation (GM)**: Strategically altering arrival times to increase and decrease glitches on specific nodes
- Circuit parsing and analysis for various cryptographic S-boxes and benchmark circuits
- Support for transition time considerations and timing analysis
- Integration with Cadence design tools for simulation and verification

## System Requirements

### Operating System
- Linux-based system (Ubuntu 18.04+ recommended)
- The code is designed to work with Cadence design tools installed in the home directory

### Python Version
- Python 3.6 or higher

### Required Python Packages

Install the following packages using pip:

```bash
# Core scientific computing packages
pip install numpy
pip install matplotlib
pip install scipy

# Optimization framework (GPKit requires additional setup)
pip install gpkit

# Standard library packages (usually pre-installed)
# - os, sys, re, shutil, csv, pickle, time, random, itertools, inspect
```

### GPKit Installation and Setup

GPKit is a geometric programming optimization framework that requires additional setup:

1. **Install GPKit**:
   ```bash
   pip install gpkit
   ```

2. **Install a solver** (GPKit requires an external solver):
   - **Free option**: Install CVXOPT
     ```bash
     pip install cvxopt
     ```
   - **Commercial option**: MOSEK (requires license)
     ```bash
     pip install mosek
     # You'll need to obtain and install a MOSEK license
     ```

3. **Verify GPKit installation**:
   ```python
   import gpkit
   print(gpkit.__version__)
   ```

### External Tools Required

The code expects the following directory structure in your home directory:

```
~/cadence/digital_design/
├── synthesis_4/
│   ├── circuit_files/
│   ├── simulation_results/
│   └── auxillary_files/

```


## Configuration

### Circuit Selection
Edit the `circuits` variable in `main.py` to select which circuit to optimize:

```python
circuits = ["masked_skinny_sbox"]  # Current default
# Other options:
# circuits = ["c17", "c432", "c880", "c1908", "c2670", "c3540", "c5315", "c6288", "c7552"]
# circuits = ["SBOX", "SBOX_aes", "unmasked_present_sbox", "unmasked_aes_sbox"]
```

### Key Parameters
- `twall_to_be_run`: Timing wall fractions to test (default: [1.1])
- `noOfGatesToConstraint_list`: Number of critical gates to constrain (default: [20])


### Path Configuration
Update the following paths in `main.py` if your setup differs:

```python
# Update these paths to match your system
circuit_files_directory = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','circuit_files')
simulation_results_directory = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','simulation_results')
auxillary_files_directory = os.path.join(os.path.expanduser('~'),'cadence','digital_design','synthesis_4','auxillary_files')
```

## How to Run

### 1. Environment Setup
```bash
# Ensure all Python dependencies are installed
pip install numpy matplotlib scipy gpkit cvxopt
```

### 2. Prepare Input Files
Ensure you have:
- Circuit netlist genus files (`.txt` format) in the circuit_files directory
- Standard cell library files (`.v` and `.lib`) in the techfiles2 directory
- Leakage score files for the circuits you want to optimize

### 3. Initial Run - Generate AM Solution
```bash
python main.py
```

This first run will:
- Parse the circuit netlist and perform area minimization (AM)
- Generate optimized gate sizes for area minimization
- Create AM result files in the simulation results directory

### 4. Simulate AM Results and Generate VCDs

After obtaining the AM solution, you need to:

1. **Functional Simulation**: 
   - Use the generated AM files from the results folder
   - Run functional simulation with your testbench
   - Generate VCD files for functional verification

2. **AM Simulation**:
   - Simulate the area-minimized circuit with the optimized gate sizes
   - Generate VCD files for the AM simulation
   - This validates the timing and functionality of the optimized circuit

### 5. Update Leakage Scores
After generating VCDs from both simulations:
- Update leakage scores for both AM and functional simulations
- Place the updated leakage score files in the circuit_files directory
- These updated scores will be used for the next optimization phase

### 6. Second Run - Generate GM Solution
```bash
python main.py
```

This second run will:
- Use the updated leakage scores from step 5
- Perform glitch modification (GM) optimization
- Generate GM solution with strategically altered arrival times
- Create GM result files optimized for glitch manipulation

### 7. Generate GM VCDs and Analyze Leakage
After obtaining the GM solution:

1. **Generate GM VCDs**:
   - Simulate the GM-optimized circuit
   - Generate VCD files from the GM results folder

2. **Run PLAN Tool**:
   - Use the generated VCDs with the PLAN (Power and Leakage ANalysis) tool
   - Analyze the leakage characteristics of the GM-optimized circuit
   - Compare leakage results between functional, AM, and GM implementations

### 8. Monitor Output
Throughout the process, the script will:
- Print progress information to the console
- Generate optimized netlists and library files
- Create simulation results in the specified output directories
- Generate summary files with optimization results

## Output Files

The script generates the following outputs in the simulation results directory:

```
simulation_results/
└── [circuit_name]/
    └── [circuit_name]_[run_number]/
        ├── AM/                    # Area Minimization results
        │   ├── AMsizes.txt       # Optimized gate sizes
        │   ├── new_verilog_*.v   # Generated Verilog netlist
        │   ├── new_lib_*.lib     # Generated library file
        │   └── [circuit_name]_results/  # Simulation outputs
        ├── GM/                    # Glitch Minimization results
        │   ├── GMsizes.txt       # Optimized gate sizes
        │   ├── new_verilog_*.v   # Generated Verilog netlist
        │   └── new_lib_*.lib     # Generated library file
        ├── AM_summary.txt         # Area minimization summary
        └── summary.txt           # Overall optimization summary
```

## Complete Workflow Summary

The optimization process follows this sequence:

1. **Initial Setup** → Prepare genus files and leakage scores
2. **AM Optimization** → Run main.py to get area-minimized solution
3. **AM Simulation** → Simulate AM results and generate functional/AM VCDs
4. **Leakage Update** → Update leakage scores in circuit_files directory
5. **GM Optimization** → Run main.py again for glitch modification
6. **GM Analysis** → Generate GM VCDs and run PLAN tool for leakage analysis
7. **Results Comparison** → Compare leakage characteristics across all implementations

## External Tools Integration

### PLAN Tool
- **Purpose**: Power and Leakage ANalysis tool for security evaluation
- **Input**: VCD files from GM simulation
- **Output**: Detailed leakage analysis and security metrics
- **Usage**: Run after generating GM VCDs to evaluate the effectiveness of glitch modification

### Simulation Tools
- **Testbench**: Required for functional verification of optimized circuits
- **VCD Generation**: Essential for both timing validation and leakage analysis
- **Integration**: Works with Cadence simulation environment

## Common Issues and Troubleshooting

### 1. Import Errors
- **Problem**: `ModuleNotFoundError` for custom modules
- **Solution**: Ensure you're running the script from the `GM-GP Code` directory

### 2. GPKit Solver Issues
- **Problem**: GPKit cannot find a solver
- **Solution**: Install CVXOPT (`pip install cvxopt`) or configure MOSEK

### 3. Path Issues
- **Problem**: FileNotFoundError for input files
- **Solution**: Create the required directory structure and place input files correctly

### 4. Memory Issues
- **Problem**: Script crashes with memory errors
- **Solution**: The script sets `sys.setrecursionlimit(10000000)` - reduce this value if needed

### 5. Optimization Convergence
- **Problem**: GP optimization fails to converge
- **Solution**: Adjust timing constraints (`twall_to_be_run`) or area constraints (`excessP_list`)


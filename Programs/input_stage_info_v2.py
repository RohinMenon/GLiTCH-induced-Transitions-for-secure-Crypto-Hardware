import numpy as np
import re
from operator import itemgetter
import sys

np.set_printoptions(threshold=sys.maxsize)

def expand_bus_signals(signal):
    """Helper function to expand bus signals into individual bits."""
    if '[' in signal:
        # Extract bus range
        base_name = signal.split('[')[0].strip()
        range_str = signal[signal.find('[')+1:signal.find(']')]
        high, low = map(int, range_str.split(':'))
        # Generate individual bit names
        return [f"{base_name}[{i}]" for i in range(high, low-1, -1)]
    return [signal]

def input_stage_info_v2(netlist_file_path):
    list_of_in_outs = []
    in_outs = []
    in_outs_of_this_gate = []
    instance_name = []
    inputs = []
    outputs = []
    output_node_map = {}
    instance_map = {}

    current_gates = []
    to_be_checked = []
    outputs_so_far = []
    current_gates_temp = []

    try:
        with open(netlist_file_path, "r") as file:
            contents = file.readlines()

        # Find input declarations
        for i in range(len(contents)):
            if "input" in contents[i] and "//" not in contents[i]:
                input_start = i
                break

        # Process input declarations
        input_declarations = []
        i = input_start
        while i < len(contents):
            line = contents[i].strip()
            if ";" in line:
                input_declarations.append(line)
                break
            input_declarations.append(line)
            i += 1

        # Extract and expand bus inputs
        input_text = ' '.join(input_declarations)
        input_text = input_text.replace('input', '').replace(';', '').strip()
        
        # Handle bus declarations first
        bus_declarations = re.findall(r'\[\d+:\d+\]\s*\w+', input_text)
        for decl in bus_declarations:
            inputs.extend(expand_bus_signals(decl))
            input_text = input_text.replace(decl, '')
        
        # Handle remaining single-bit declarations
        single_bits = [x.strip() for x in input_text.split(',') if x.strip() and '[' not in x]
        inputs.extend(single_bits)
        
        # Remove empty strings and clean up
        inputs = [x.strip() for x in inputs if x.strip()]

        # Similar process for outputs
        for i in range(len(contents)):
            if "output" in contents[i] and "//" not in contents[i]:
                output_start = i
                break

        output_declarations = []
        i = output_start
        while i < len(contents):
            line = contents[i].strip()
            if ";" in line:
                output_declarations.append(line)
                break
            output_declarations.append(line)
            i += 1

        output_text = ' '.join(output_declarations)
        output_text = output_text.replace('output', '').replace(';', '').strip()
        
        # Handle bus declarations first
        bus_declarations = re.findall(r'\[\d+:\d+\]\s*\w+', output_text)
        for decl in bus_declarations:
            outputs.extend(expand_bus_signals(decl))
            output_text = output_text.replace(decl, '')
        
        # Handle remaining single-bit declarations
        single_bits = [x.strip() for x in output_text.split(',') if x.strip() and '[' not in x]
        outputs.extend(single_bits)
        
        # Remove empty strings and clean up
        outputs = [x.strip() for x in outputs if x.strip()]

        outputs_so_far = list(inputs)

        # Find wire and gate sections
        wire_end = 0
        gate_end = 0
        for i in range(len(contents)):
            if "wire" in contents[i]:
                wire_end = i
            if "endmodule" in contents[i]:
                gate_end = i - 1

        while ';' not in contents[wire_end]:
            wire_end += 1

        gate_start = wire_end + 1

        while contents[gate_start] == '\n':
            gate_start += 1

        while contents[gate_end] == '\n':
            gate_end -= 1

        # Count number of gates
        N = sum(1 for i in range(gate_start, gate_end + 1) if ';' in contents[i])

        # Process gates
        to_be_checked = list(range(N))
        gates_arrival_time = np.zeros(shape=(N + 1, 2), dtype=int)
        node_level = np.zeros(shape=N + 1, dtype=int)

        for i in inputs:
            output_node_map[i] = N

        i = gate_start
        j = 0
        flag = 1
        while i <= gate_end:
            if contents[i].strip():
                instance_name.append(contents[i].split('(')[0].split()[1].strip())
                temp = contents[i].rstrip(';\n').split('(')[1].rstrip(')').split(',')
                temp.reverse()
                while temp:
                    sig = temp.pop().strip()
                    # Handle bus bits in port connections
                    if '[' in sig:
                        sig = sig.strip()  # Clean up any whitespace
                    in_outs_of_this_gate.append(sig)

                in_outs.append(in_outs_of_this_gate)
                no_of_inputs = len(in_outs[j]) - 1
                output_node_map[in_outs[j][0]] = j

                for f in in_outs[j][1:]:
                    if f not in inputs:
                        flag = 0
                        break
                if flag:
                    node_level[j] = 1
                    current_gates.append(j)
                    to_be_checked.remove(j)
                    outputs_so_far.append(in_outs[j][0].strip())
                
                flag = 1

                if ";" not in contents[i]:
                    i += 1

                j += 1
                in_outs_of_this_gate = []
            i += 1

        # Level processing
        flag = 1
        level = 2
        while current_gates:
            for i in current_gates:
                for j in to_be_checked:
                    if in_outs[i][0].strip() in in_outs[j][1:]:
                        for k in in_outs[j][1:]:
                            if k not in outputs_so_far:
                                flag = 0
                                break

                        if flag and j not in current_gates_temp:
                            current_gates_temp.append(j)
                    flag = 1
                    
            current_gates = list(current_gates_temp)
            for u in current_gates_temp:
                to_be_checked.remove(u)
                outputs_so_far.append(in_outs[u][0])

            current_gates_temp = []
            for i in current_gates:
                gates_connected_to_input = itemgetter(*in_outs[i][1:])(output_node_map)
                node_level[i] = level

            level += 1

        # Prepare summary
        summary_to_be_printed = np.zeros(shape=(N, 2), dtype=int)
        for i in range(N):
            if isinstance(itemgetter(*in_outs[i][1:])(output_node_map), tuple):
                summary_to_be_printed[i, 0] = np.amin(node_level[list(itemgetter(*in_outs[i][1:])(output_node_map))])
                summary_to_be_printed[i, 1] = np.amax(node_level[list(itemgetter(*in_outs[i][1:])(output_node_map))])
            else:
                summary_to_be_printed[i, 0] = np.amin(node_level[itemgetter(*in_outs[i][1:])(output_node_map)])
                summary_to_be_printed[i, 1] = np.amax(node_level[itemgetter(*in_outs[i][1:])(output_node_map)])

        return summary_to_be_printed

    except IOError:
        print("Netlist file not found")

if __name__ == "__main__":
    result = input_stage_info(netlist_file_path)

import argparse

def parse_signals(file_path):
    signals = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                # Split by whitespace (assumes first part is the value, second part is the signal name)
                value, signal = line.split(maxsplit=1)
                signals[signal] = float(value)  # Store signal name as key and value as float
    
    return signals

def compare_signals(file1, file2):
    signals1 = parse_signals(file1)
    signals2 = parse_signals(file2)
    
    # Find all unique signal names across both files
    all_signals = set(signals1.keys()).union(signals2.keys())
    
    differences = []
    
    for signal in all_signals:
        val1 = signals1.get(signal, None)
        val2 = signals2.get(signal, None)
        
        if val1 is None:
            differences.append(f"{signal} is missing in {file1}")
        elif val2 is None:
            differences.append(f"{signal} is missing in {file2}")
        elif val1 != val2:
            differences.append(f"Mismatch for {signal}: {file1}={val1}, {file2}={val2}")
    
    return differences

if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(description='Pre-silicon power side-channel analysis using PLAN')

    my_parser.add_argument('File1',
                            metavar='file1',
                            type=str)
    my_parser.add_argument('File2',
                            metavar='file2',
                            type=str)
    # parsing the arguments
    args = my_parser.parse_args()

    # File paths for comparison
    file1 = args.File1
    file2 = args.File2

    # Perform the comparison
    diffs = compare_signals(file1, file2)

    # Output the results
    if diffs:
        print("Differences found:")
        for diff in diffs:
            print(diff)
    else:
        print("No differences found.")

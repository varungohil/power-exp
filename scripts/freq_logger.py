import csv
import time
import argparse
import subprocess

#def get_core_freq(core):
#    """Read current frequency for a given CPU core"""
#    try:
#        with open(f"/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_cur_freq") as f:
#            return int(f.read().strip()) / 1000  # Convert KHz to MHz
#    except:
#        return 0


#def get_core_freq(core):
#    """Read current frequency for a given CPU core using cpupower"""
#    try:
#        cmd = f"cpupower -c {core} frequency-info -f"
#        result = subprocess.run(cmd.split(), capture_output=True, text=True)
#        # Extract frequency value from output
#        freq_line = result.stdout.strip()
#        value = float(freq_line.split()[-2])  # Get the number
#        unit = freq_line.split()[-1].lower()  # Get the unit (MHz or GHz)
#        
#        # Convert everything to MHz for consistency
#        if 'ghz' in unit:
#            value = value * 1000  # Convert GHz to MHz
#        return value
#    except Exception as e:
#        print(f"Error reading frequency for core {core}: {e}")
#        return 0


def get_core_freq(core):
    """Read current frequency for a given CPU core using cpupower"""
    try:
        cmd = f"cpupower -c {core} frequency-info"
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        
        # Look for the asserted frequency line
        for line in result.stdout.split('\n'):
            if "current CPU frequency" in line and "asserted by call to kernel" in line:
                # Extract the frequency value and unit
                parts = line.split(':')[1].strip().split()
                value = float(parts[0])
                unit = parts[1].lower()
                
                # Convert to MHz if needed
                if 'ghz' in unit:
                    value = value * 1000  # Convert GHz to MHz
                return value
        
        return 0  # Return 0 if frequency not found
    except Exception as e:
        print(f"Error reading frequency for core {core}: {e}")
        return 0

# ... existing code ...


def main():
    parser = argparse.ArgumentParser(prog='freq_logger')
    parser.add_argument('-f', '--filename', help='Output CSV file path')    
    parser.add_argument('-d', '--duration', type=int, help='Duration in seconds') 
    parser.add_argument('-c', '--cores', help='Comma-separated list of cores to monitor')
    parser.add_argument('-i', '--interval', type=float, default=0.5, help='Sampling interval in seconds')
    args = parser.parse_args()

    cores = [int(x) for x in args.cores.split(',')]
    
    with open(args.filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write header with core numbers
        header = ['timestamp'] + [f'core_{core}_freq' for core in cores]
        csv_writer.writerow(header)

        start_time = time.time()
        try:
            while time.time() - start_time < args.duration:
                timestamp = time.time()
                freqs = [get_core_freq(core) for core in cores]
                row = [timestamp] + freqs
                csv_writer.writerow(row)
                csvfile.flush()
                time.sleep(args.interval)

        except KeyboardInterrupt:
            print("Interrupted. Exiting.")

if __name__ == "__main__":
    main() 

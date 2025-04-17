import csv
import time
import argparse
import subprocess

def get_uncore_freq(core):
    """Read current uncore frequency"""
    command = f"sudo rdmsr 0x621"
    result = subprocess.check_output(command, shell=True)
    return result.decode().strip()



def main():
    parser = argparse.ArgumentParser(prog='freq_logger')
    parser.add_argument('-f', '--filename', help='Output CSV file path')    
    parser.add_argument('-d', '--duration', type=int, help='Duration in seconds') 
    args = parser.parse_args()

    
    with open(args.filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write header with core numbers
        header = ['timestamp', 'uncore_freq']
        csv_writer.writerow(header)

        start_time = time.time()
        try:
            while time.time() - start_time < args.duration:
                timestamp = time.time()
                row = [timestamp, get_uncore_freq()]
                csv_writer.writerow(row)
                # csvfile.flush()
                # time.sleep(args.interval)

        except KeyboardInterrupt:
            print("Interrupted. Exiting.")

if __name__ == "__main__":
    main() 

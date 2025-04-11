import csv
import time
import argparse
import psutil

def get_cpu_utilization(core):
    """Get CPU utilization for a specific core."""
    return psutil.cpu_percent(interval=0.1, percpu=True)[core]

def main():
    parser = argparse.ArgumentParser(
                        prog='cpu_logger')
    parser.add_argument('-f', '--filename', required=True,
                      help='Output CSV file path')
    parser.add_argument('-d', '--duration', required=True,
                      help='Duration to log in seconds')
    parser.add_argument('-c', '--cores', required=True,
                      help='Comma-separated list of core numbers to monitor')
    parser.add_argument('-s', '--sleeptime', default=1,
                      help='Sleep time between measurements in seconds')
    
    args = parser.parse_args()
    output_file = args.filename
    cores = [int(core) for core in args.cores.split(',')]
    
    # Validate core numbers
    num_cores = psutil.cpu_count()
    if any(core >= num_cores for core in cores):
        print(f"Error: Core numbers must be between 0 and {num_cores-1}")
        return

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header with core numbers
        header = ['timestamp'] + [f'cpu_core_{core}' for core in cores]
        csv_writer.writerow(header)

        start_time = time.time()
        try:
            while time.time() - start_time < int(args.duration):
                timestamp = time.time()
                # Get utilization for each requested core
                cpu_info = [get_cpu_utilization(core) for core in cores]
                csv_info = [timestamp] + cpu_info
                csv_writer.writerow(csv_info)
                csvfile.flush()
                # time.sleep(float(args.sleeptime))

        except KeyboardInterrupt:
            print("Interrupted. Exiting.")

if __name__ == "__main__":
    main() 
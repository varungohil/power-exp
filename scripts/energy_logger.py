import csv
import time
import argparse
import subprocess

def run_powercap_info(zone):
    command = f"sudo powercap-info -p intel-rapl -z {zone} -j" 
    result = subprocess.check_output(command, shell=True)
    return result.decode().strip()

def main():
    parser = argparse.ArgumentParser(
                        prog='energy_logger')
    parser.add_argument('-f','--filename')    
    parser.add_argument('-d','--duration') 
    parser.add_argument('-n','--numsockets') 
    # parser.add_argument('-s','--sleeptime')           
    args = parser.parse_args()
    output_file = args.filename

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['timestamp', 'energy_zone_0', 'energy_zone_1'])

        start_time = time.time()
        try:
            while time.time() - start_time < int(args.duration):
                timestamp = time.time()
                power_info = [ run_powercap_info(x) for x in range(int(args.numsockets))]
                # power_info_0 = run_powercap_info(0)
                # power_info_1 = run_powercap_info(1)
                csv_info = [timestamp]
                csv_info.extend(power_info)
                csv_writer.writerow(csv_info)
                # csvfile.flush()
                # time.sleep(1)

            csvfile.flush()
        except KeyboardInterrupt:
            print("Interrupted. Exiting.")

if __name__ == "__main__":
    main()
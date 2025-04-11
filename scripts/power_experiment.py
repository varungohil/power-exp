import argparse
import threading
import time
import sys
sys.path.append("../cloudlab-lib")
import cloudlab_lib

def get_cpu_topology(node, cl):
    """Get CPU topology for a node and return a dictionary mapping sockets to their cores."""
    # Get CPU info using lscpu
    cmd = "lscpu -p=cpu,node | grep -v '#'"
    stdout, stderr, exit_status = cl.run_on_node(node, cmd)
    
    if exit_status != 0:
        raise Exception(f"Failed to get CPU topology: {stderr}")
    
    # Parse the output to create socket -> cores mapping
    socket_cores = {}
    for line in stdout:
        cpu, socket = map(int, line.strip().split(','))
        if socket not in socket_cores:
            socket_cores[socket] = []
        socket_cores[socket].append(cpu)
    
    return socket_cores

def run_busy_loop(node, core, duration, cl):
    """Run busy_loop.py on a specific core."""

    cmd = f"""
    cd /users/varuncg/power-exp/scripts;
    taskset -c {core} python3 busy_loop.py -d {duration}
    """
    return cl.run_on_node(node, cmd)

def run_energy_logger(node, socket, duration, cl, filename):
    """Run energy_logger.py on a specific socket."""
    cmd = f"""
    cd /users/varuncg/power-exp/scripts;
    taskset -c {socket} python3 energy_logger.py -d {duration} -n 2 -f {filename}
    """
    return cl.run_on_node(node, cmd)

def main():
    parser = argparse.ArgumentParser(description='Power experiment script')
    parser.add_argument('--config', required=True, help='Path to server config JSON file')
    parser.add_argument('--disable-intelpstate', action='store_true', help='Disable Intel P-state driver')
    parser.add_argument('--setup', action='store_true', help='Setup the environment')
    parser.add_argument('--run', action='store_true', help='Run the experiment')
    parser.add_argument('--utilization', type=float, default=0.5, help='CPU utilization (0.0 to 1.0)')
    parser.add_argument('--duration', type=int, default=60, help='Duration of experiment in seconds')
    parser.add_argument('--node', default='node-0', help='Target node to run experiment on')
    
    args = parser.parse_args()
    
    # Initialize CloudLab agent
    cl = cloudlab_lib.CloudLabAgent(args.config)
    
    # Disable Intel P-state if requested
    if args.disable_intelpstate:
        print("Disabling Intel P-state driver...")
        cl.turn_intel_pstate_driver("all", "off")
        time.sleep(5)  # Wait for changes to take effect
    
    # Setup if requested
    if args.setup:
        print("Setting up environment...") 
        cl.install_deps("all")
        # Clone repository
        cl.run("all", "git clone https://github.com/varungohil/power-exp.git --recurse-submodules")
        
        # Configure power settings
        cl.turn_turboboost("all", "off", "acpi", exit_on_err=True)
        cl.run("all", "sudo ethtool -K enp94s0f0 ntuple on")
        cl.run("all", "sudo apt-get install chrony -y")

    if args.run:
    
        # Get CPU topology
        print("Getting CPU topology...")
        socket_cores = get_cpu_topology(args.node, cl)
        print(f"CPU topology: {socket_cores}")
        

        cl.run(args.node, "mkdir -p energy")
        # Set power governor to userspace and set frequencies
        print("Setting power governor and frequencies...")
        cl.set_power_governor(args.node, "userspace")
        for socket in socket_cores:
            cl.set_frequency(args.node, ",".join(map(str, socket_cores[socket])), "0.8GHz")
        
        # Calculate number of cores to use based on utilization
        socket1_cores = socket_cores[1]  # Get cores from socket 1
        num_cores_to_use = int(len(socket1_cores) * args.utilization)
        cores_to_use = socket1_cores[:num_cores_to_use]
        
        # Create all threads
        print("Creating threads...")
        threads = []
        
        # Create energy logger thread
        filename = "energy/energy.csv"
        energy_thread = threading.Thread(
            target=run_energy_logger,
            args=(args.node, socket_cores[0][0], args.duration, cl, filename)
        )
        threads.append(energy_thread)
        
        # Create busy loop threads
        print(f"Creating busy loop threads for {num_cores_to_use} cores...")
        for core in cores_to_use:
            thread = threading.Thread(
                target=run_busy_loop,
                args=(args.node, core, args.duration, cl)
            )
            threads.append(thread)
        
        # Start all threads together
        print("Starting all threads...")
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        print("Waiting for experiment to complete...")
        for thread in threads:
            thread.join()
        
        print("Experiment completed!")

if __name__ == "__main__":
    main() 

import time
import argparse
import multiprocessing
import os

def busy_loop(duration, core_id=None):
    if core_id is not None:
        os.sched_setaffinity(0, {core_id})
    
    start_time = time.time()
    while time.time() - start_time < duration:
        continue

def main():
    parser = argparse.ArgumentParser(prog='busy_loop.py')
    parser.add_argument('-d', '--duration', required=True,
                      help='Duration to log in seconds')
    parser.add_argument('-c', '--cores', required=True,
                      help='Comma-separated list of core IDs to use')
    
    args = parser.parse_args()
    duration = int(args.duration)
    core_ids = [int(core) for core in args.cores.split(',')]
    
    processes = []
    for core_id in core_ids:
        p = multiprocessing.Process(target=busy_loop, args=(duration, core_id))
        processes.append(p)
        p.start()
    
    # Wait for all processes to complete
    for p in processes:
        p.join()

if __name__ == "__main__":
    main() 
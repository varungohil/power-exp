
import time
import argparse

def main():
    parser = argparse.ArgumentParser(
                        prog='busy_loop.py')
    parser.add_argument('-d', '--duration', required=True,
                      help='Duration to log in seconds')
    
    args = parser.parse_args()

    start_time = time.time()
    while time.time() - start_time < int(args.duration):
        continue

if __name__ == "__main__":
    main() 
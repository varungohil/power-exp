import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
from latexify import *

def handle_energy_counter_overflow(series, max_value=2**32):
    """Handle counter overflow by detecting large negative differences"""
    diff = series.diff()
    # Detect where overflow might have occurred (large negative values)
    overflow_idx = diff < -max_value/2
    # Calculate the actual difference accounting for overflow
    corrected_diff = diff.copy()
    corrected_diff[overflow_idx] += max_value
    return corrected_diff

def calculate_power(csv_file):
    """Calculate power consumption from energy measurements"""
    # Read CSV file
    df = pd.read_csv(csv_file)
    
    # Convert timestamp to float if it's string
    df['timestamp'] = pd.to_numeric(df['timestamp'])
    
    # Calculate time differences
    time_diff = df['timestamp'].diff()
    
    # Handle energy counter overflows for each zone
    energy_cols = [col for col in df.columns if col.startswith('energy_zone_')]
    powers = {}
    
    for zone in energy_cols:
        # Calculate energy differences handling overflow
        energy_diff = handle_energy_counter_overflow(df[zone])
        
        # Calculate power (energy/time) in Watts
        # Convert from microjoules to joules (divide by 1e6)
        power = energy_diff / time_diff / 1e6
        powers[f'power_{zone[7:]}'] = power
    
    # Add power columns to dataframe
    for col_name, power_values in powers.items():
        df[col_name] = power_values
    
    return df

def combine_power_runs(run_files):
    """Combine power measurements from multiple runs"""
    # Read and calculate power for each run
    power_dfs = [calculate_power(f) for f in run_files]
    
    # Find minimum length among all runs
    min_length = min(len(df) for df in power_dfs)
    
    # Create arrays for each socket's power values
    socket0_power = np.array([df['power_zone_0'].iloc[:min_length].values for df in power_dfs])
    socket1_power = np.array([df['power_zone_1'].iloc[:min_length].values for df in power_dfs])
    
    # Calculate mean and std across runs for each time point
    socket0_mean = np.mean(socket0_power, axis=0)
    socket0_std = np.std(socket0_power, axis=0)
    socket1_mean = np.mean(socket1_power, axis=0)
    socket1_std = np.std(socket1_power, axis=0)
    
    # Create a new dataframe with the combined results
    combined_df = pd.DataFrame({
        'timestamp': power_dfs[0]['timestamp'].iloc[:min_length],
        'power_zone_0_mean': socket0_mean,
        'power_zone_0_std': socket0_std,
        'power_zone_1_mean': socket1_mean,
        'power_zone_1_std': socket1_std
    })
    
    return combined_df

def main():
    # Get all energy files
    energy_files = glob.glob('../data/energy/energy_socket*-*_util-*_run-*.csv')
    
    # Group files by utilization level and socket frequency
    utilizations = set()
    socket_freqs = set()
    for file in energy_files:
        # Extract utilization and socket frequency from filename
        parts = os.path.basename(file).split('_')
        util = float(parts[2].split('-')[1])
        freq = parts[1].split('-')[1]
        utilizations.add(util)
        socket_freqs.add(freq)
    
    # Sort utilizations and frequencies
    utilizations = sorted(utilizations)
    socket_freqs = sorted(socket_freqs)
    
    # Calculate global y-axis limits
    global_min_power = float('inf')
    global_max_power = float('-inf')
    
    for active_socket in [0, 1]:
        for util in utilizations:
            for freq in ["0.8GHz", "1.5GHz", "2.2GHz"]:
                # Find all runs for this configuration
                passive_socket = 1 - active_socket
                pattern = f'../data/energy/energy_socket{passive_socket}-{freq}_util-{util:.1f}_run-*.csv'
                matching_files = glob.glob(pattern)
                
                if not matching_files:
                    continue
                
                # Combine power measurements across runs
                combined_df = combine_power_runs(matching_files)
                
                # Check both socket power values
                for socket in [0, 1]:
                    power_values = combined_df[f'power_zone_{socket}_mean']
                    
                    # Calculate quartiles and IQR to exclude outliers
                    Q1 = power_values.quantile(0.25)
                    Q3 = power_values.quantile(0.75)
                    IQR = Q3 - Q1
                    
                    # Define bounds for outliers (1.5 * IQR is a common threshold)
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    # Filter out outliers
                    filtered_power = power_values[(power_values >= lower_bound) & (power_values <= upper_bound)]
                    
                    # Update global min/max with filtered values
                    global_min_power = min(global_min_power, filtered_power.min())
                    global_max_power = max(global_max_power, filtered_power.max())

    # Add some padding to the limits
    padding = (global_max_power - global_min_power) * 0.1
    global_min_power -= padding
    global_max_power += padding
     
    # Create side-by-side plots for each active socket and utilization level
    for active_socket in [0, 1]:
        passive_socket = 1 - active_socket
        
        for util in utilizations:
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 6))
            
            # Plot for each frequency
            for freq in ["0.8GHz", "1.2GHz", "1.5GHz", "1.8GHz", "2.0GHz", "2.2GHz"]:
                # Find all runs for this configuration
                pattern = f'../data/energy/energy_socket{passive_socket}-{freq}_util-{util:.1f}_run-*.csv'
                matching_files = glob.glob(pattern)
                
                if not matching_files:
                    continue
                
                # Combine power measurements across runs
                combined_df = combine_power_runs(matching_files)
                
                # Plot socket 0 power with error bars
                time = combined_df['timestamp'] - combined_df['timestamp'].iloc[0]
                ax1.errorbar(time, 
                           combined_df['power_zone_0_mean'],
                           yerr=combined_df['power_zone_0_std'],
                           label=f'Frequency of socket {passive_socket} = {freq}')
                
                # Plot socket 1 power with error bars
                ax2.errorbar(time,
                           combined_df['power_zone_1_mean'],
                           yerr=combined_df['power_zone_1_std'],
                           label=f'Frequency of socket {passive_socket} = {freq}')
            
            # Set titles and labels for socket 0 plot
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Power Consumption (W)')
            ax1.set_title(f'Socket 0 Power Consumption\n')
            ax1.legend()
            ax1.grid(True)
            ax1.set_ylim(global_min_power, global_max_power)
            
            # Set titles and labels for socket 1 plot
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Power Consumption (W)')
            ax2.set_title(f'Socket 1 Power Consumption\n')
            ax2.legend()
            ax2.grid(True)
            ax2.set_ylim(global_min_power, global_max_power)
            
            # Add overall title
            fig.suptitle(f'Power Consumption | Active Socket: {active_socket} | Active Socket Freq = 1.2GHz | Active Socket Utilization = {util*100}%', fontsize=16)
            
            # Adjust layout and save
            plt.tight_layout()
            saveimage(f'power_side_by_side_active{active_socket}_util_{util:.1f}', folder='../data/plots/', extension='png')
            plt.close()

if __name__ == "__main__":
    main() 

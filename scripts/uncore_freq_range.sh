# Read the current uncore frequency settings
value=$(sudo rdmsr 0x620)

# Extract min and max values
max_ratio=$((0x$value & 0xFF))
min_ratio=$(((0x$value >> 8) & 0xFF))

# Calculate actual frequencies
max_freq=$(($max_ratio * 100))
min_freq=$(($min_ratio * 100))

echo "Uncore frequency range: $min_freq MHz to $max_freq MHz"
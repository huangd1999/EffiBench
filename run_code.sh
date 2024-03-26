#!/bin/bash

# Function to calculate memory usage in MB*seconds
calculate_memory_usage() {
    local dat_file=$1
    awk 'BEGIN { 
        prev_time = 0; 
        prev_mem_mb = 0; 
        mem_time_mb_s = 0;
    }
    NR>1 {
        mem_in_mb = $2;
        timestamp = $3;
        
        if (prev_time > 0) {
            time_interval_s = timestamp - prev_time;
            mem_time_mb_s += (prev_mem_mb + mem_in_mb) / 2 * time_interval_s;
        }
        
        prev_time = timestamp;
        prev_mem_mb = mem_in_mb;
    }
    END {
        printf "%.2f\n", mem_time_mb_s;
    }' "$dat_file"
}

# Specify the file and output path
# completion_file="./tmp/tmp.py"
# completion_dat_file="./tmp/tmp.dat"
completion_file="$1"
completion_dat_file="$2"

# Initialize max execution time
max_execution_time=5

# Execute the specified file
echo "Executing $completion_file"
error_output=$(mktemp)
start_time=$(date +%s%N)
rm -f "$completion_dat_file"
timeout "$max_execution_time" mprof run --interval 0.0001 --output "$completion_dat_file" "$completion_file" 2> "$error_output"
end_time=$(date +%s%N)
execution_time=$(( (end_time - start_time) / 1000000 ))
exit_status=$?

# Check execution status
echo "Execution status: $exit_status"
if [ $exit_status -ne 0 ] || [ -s "$error_output" ]; then
    echo "Execution failed or errors were reported for $completion_file. Removing .dat file."
    rm -f "$completion_dat_file"
elif [ -f "$completion_dat_file" ]; then
    mem_usage_mb_s=$(calculate_memory_usage "$completion_dat_file")
    echo "Memory usage (MB*seconds): $mem_usage_mb_s"
else
    echo "Execution completed but no .dat file found for $completion_file."
fi

# Clean up
rm -f "$error_output"

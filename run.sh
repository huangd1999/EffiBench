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


models=("gpt-3.5-turbo-0301" "canonical_solution")

for model in "${models[@]}"; do
    completion_tmp_dat_directory="./${model}_dat"
    rm -rf "$completion_tmp_dat_directory"
    mkdir -p "$completion_tmp_dat_directory"
    completion_directory="./${model}_tmp"
    max_execution_time=5
    declare -A completion_memory_usage
    successful_execution_count_completion=0
    total_execution_time_completion=0
    total_completion_execution_memory=0

    # Traverse completion_tmp directory and calculate execution time and memory usage
    for completion_file in "$completion_directory"/*.py; do
        if [ -f "$completion_file" ]; then
            echo "Executing $completion_file"

            error_output=$(mktemp)

            start_time=$(date +%s%N)
            timeout "$max_execution_time" mprof run --interval 0.0001 --output "$completion_tmp_dat_directory/$(basename "$completion_file" .py).dat" "$completion_file" 2> "$error_output"
            end_time=$(date +%s%N)
            execution_time=$(( (end_time - start_time) / 1000000 ))
            exit_status=$?

            mprof_file="$completion_tmp_dat_directory/$(basename "$completion_file" .py).dat"
            echo "Execution status: $exit_status"

            if [ $exit_status -ne 0 ] || [ -s "$error_output" ]; then
                echo "Execution failed or errors were reported for $completion_file. Removing .dat file."
                rm -f "$mprof_file"
            elif [ -f "$mprof_file" ]; then
                mem_usage_mb_s=$(calculate_memory_usage "$mprof_file")
                file_name=$(basename "$completion_file")
                completion_memory_usage["$file_name"]=$mem_usage_mb_s
                total_completion_execution_memory=$(echo "$total_completion_execution_memory + $mem_usage_mb_s" | bc)
                total_execution_time_completion=$((total_execution_time_completion + execution_time))
                successful_execution_count_completion=$((successful_execution_count_completion + 1))
            else
                echo "Execution completed but no .dat file found for $completion_file."
            fi

            rm -f "$error_output"
        fi
    done
done


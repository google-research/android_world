#!/bin/bash

# AndroidWorld Benchmark Runner Script
# This script sets up the environment and runs the benchmark with RandomAgent
# Usage: ./run_benchmark.sh [fast|full] [task_name]

set -e  # Exit on any error

# Parse command line arguments
MODE="full"  # default
SPECIFIC_TASK=""

# Help function
show_help() {
    cat << EOF
AndroidWorld Benchmark Runner
=============================

Usage: ./run_benchmark.sh [MODE] [TASK_NAME]
       ./run_benchmark.sh [TASK_NAME]
       ./run_benchmark.sh --help

MODES:
  fast    Run minimal_task_runner.py (quick test)
  full    Run full benchmark with RandomAgent (default)

EXAMPLES:
  ./run_benchmark.sh                           # Full benchmark with default tasks
  ./run_benchmark.sh fast                      # Fast mode with random task
  ./run_benchmark.sh fast ContactsAddContact   # Fast mode with specific task
  ./run_benchmark.sh full ClockStopWatchRunning # Full mode with specific task
  ./run_benchmark.sh ContactsAddContact        # Full mode with specific task (shorthand)

AVAILABLE TASKS:
  ContactsAddContact, ClockStopWatchRunning, and many more...
  (See AndroidWorld documentation for full task list)

OUTPUT:
  Results are saved to ./runs/ with timestamp:
  - benchmark_summary_YYYYMMDD_HHMMSS.txt (parsed summary)
  - benchmark_output_YYYYMMDD_HHMMSS.log (full output)

EOF
}

if [ $# -gt 0 ]; then
    case $1 in
        --help|-h|help)
            show_help
            exit 0
            ;;
        fast|full)
            MODE=$1
            if [ $# -gt 1 ]; then
                SPECIFIC_TASK=$2
            fi
            ;;
        *)
            # First argument is a task name, use full mode
            SPECIFIC_TASK=$1
            ;;
    esac
fi

echo "🚀 Starting AndroidWorld Benchmark Setup..."
echo "📋 Mode: $MODE"
if [ -n "$SPECIFIC_TASK" ]; then
    echo "🎯 Specific Task: $SPECIFIC_TASK"
fi

# Add Android SDK tools to PATH
export PATH="$PATH:~/Library/Android/sdk/platform-tools"
export PATH="$PATH:~/Library/Android/sdk/emulator"

# Function to check if emulator is running
check_emulator() {
    adb devices 2>/dev/null | grep -q "emulator" && return 0 || return 1
}

# Function to wait for emulator to be ready
wait_for_emulator() {
    echo "⏳ Waiting for emulator to be ready..."
    local timeout=120  # 2 minutes timeout
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        if adb shell getprop sys.boot_completed 2>/dev/null | grep -q "1"; then
            echo "✅ Emulator is ready!"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        echo "   Waiting... (${elapsed}s/${timeout}s)"
    done
    
    echo "❌ Timeout waiting for emulator to be ready"
    return 1
}

# Function to parse and save results
parse_and_save_results() {
    local output_file=$1
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local runs_dir="./runs"
    local summary_file="$runs_dir/benchmark_summary_$timestamp.txt"
    
    # Create runs directory if it doesn't exist
    mkdir -p "$runs_dir"
    
    echo "📊 Parsing results and saving summary..."
    
    # Create summary file
    cat > "$summary_file" << EOF
AndroidWorld Benchmark Summary
==============================
Timestamp: $(date)
Mode: $MODE
Agent: random_agent
$([ -n "$SPECIFIC_TASK" ] && echo "Specific Task: $SPECIFIC_TASK" || echo "Tasks: ContactsAddContact, ClockStopWatchRunning")

TASK RESULTS:
=============
EOF

    # Parse the output for task results
    if grep -q "Running task:" "$output_file"; then
        while IFS= read -r line; do
            if [[ $line == *"Running task:"* ]]; then
                current_task=$(echo "$line" | sed 's/.*Running task: //')
                echo "" >> "$summary_file"
                echo "$current_task" >> "$summary_file"
                echo "$(printf '=%.0s' {1..${#current_task}})" >> "$summary_file"
            elif [[ $line == *"with goal"* ]]; then
                goal=$(echo "$line" | sed 's/.*with goal "//' | sed 's/".*//')
                echo "Goal: \"$goal\"" >> "$summary_file"
            elif [[ $line == *"Task Failed"* ]] || [[ $line == *"Task Passed"* ]]; then
                if [[ $line == *"Failed"* ]]; then
                    echo "Result: ❌ Failed" >> "$summary_file"
                else
                    echo "Result: ✅ Passed" >> "$summary_file"
                fi
            elif [[ $line == *"Agent did not indicate task is done"* ]]; then
                echo "Reason: Agent reached max steps without completing task" >> "$summary_file"
            elif [[ $line == *"Completed step"* ]]; then
                step_num=$(echo "$line" | grep -o 'Completed step [0-9]*' | tail -1 | grep -o '[0-9]*')
                if [ -n "$step_num" ]; then
                    last_step=$step_num
                fi
            fi
        done < "$output_file"
        
        # Add final statistics from the table
        if grep -A 10 "mean_success_rate" "$output_file" > /dev/null; then
            echo "" >> "$summary_file"
            echo "SUMMARY STATISTICS:" >> "$summary_file"
            echo "==================" >> "$summary_file"
            grep -A 20 "mean_success_rate" "$output_file" | head -10 >> "$summary_file"
        fi
    fi
    
    echo "" >> "$summary_file"
    echo "Full output saved to: benchmark_output_$timestamp.log" >> "$summary_file"
    
    # Copy full output
    cp "$output_file" "$runs_dir/benchmark_output_$timestamp.log"
    
    echo "✅ Results saved:"
    echo "   📄 Summary: $summary_file"
    echo "   📋 Full log: $runs_dir/benchmark_output_$timestamp.log"
}

# Activate conda environment
echo "🔧 Activating android_world conda environment..."
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate android_world

# Check if emulator is already running (only for full mode)
if [ "$MODE" = "full" ]; then
    if check_emulator; then
        echo "✅ Android emulator is already running"
    else
        echo "📱 Starting Android emulator..."
        
        # Kill any existing emulator processes first
        pkill -f "emulator.*AndroidWorldAvd" || true
        sleep 2
        
        # Start emulator in background
        nohup ~/Library/Android/sdk/emulator/emulator -avd AndroidWorldAvd -no-snapshot -grpc 8554 > emulator.log 2>&1 &
        EMULATOR_PID=$!
        echo "   Emulator started with PID: $EMULATOR_PID"
        
        # Wait for emulator to be ready
        if ! wait_for_emulator; then
            echo "❌ Failed to start emulator. Check emulator.log for details."
            exit 1
        fi
    fi
    
    # Verify adb connection
    echo "🔍 Checking ADB connection..."
    adb devices
fi

# Create temporary output file
TEMP_OUTPUT=$(mktemp)

# Run based on mode
if [ "$MODE" = "fast" ]; then
    echo "⚡ Running fast mode with RandomAgent..."
    if [ -n "$SPECIFIC_TASK" ]; then
        echo "🎯 Task: $SPECIFIC_TASK"
        python random_minimal_runner.py --task="$SPECIFIC_TASK" 2>&1 | tee "$TEMP_OUTPUT"
    else
        echo "🎲 Random task selection"
        python random_minimal_runner.py 2>&1 | tee "$TEMP_OUTPUT"
    fi
else
    echo "🎯 Running full benchmark with RandomAgent..."
    if [ -n "$SPECIFIC_TASK" ]; then
        echo "   Task: $SPECIFIC_TASK"
        python run.py \
            --suite_family=android_world \
            --agent_name=random_agent \
            --tasks="$SPECIFIC_TASK" \
            --n_task_combinations=1 2>&1 | tee "$TEMP_OUTPUT"
    else
        echo "   Tasks: ContactsAddContact, ClockStopWatchRunning"
        python run.py \
            --suite_family=android_world \
            --agent_name=random_agent \
            --tasks=ContactsAddContact,ClockStopWatchRunning \
            --n_task_combinations=1 2>&1 | tee "$TEMP_OUTPUT"
    fi
fi

# Parse and save results
parse_and_save_results "$TEMP_OUTPUT"

# Cleanup
rm "$TEMP_OUTPUT"

echo "🎉 Benchmark completed!"
echo "📊 Results saved to: ./runs/" 
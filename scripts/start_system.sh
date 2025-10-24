#!/bin/bash

# Complete System Launcher
# Starts both CARLA agent and DORA dataflow

set -e

echo "=================================="
echo "CARLA-DORA System Launcher"
echo "=================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "This script will start both CARLA agent and DORA dataflow"
echo "Make sure CARLA server is already running!"
echo ""

# Start DORA in background
echo "Step 1: Starting DORA dataflow..."
"$SCRIPT_DIR/start_dora.sh" &
DORA_PID=$!

# Wait a bit for DORA to initialize
sleep 3

# Start CARLA agent
echo ""
echo "Step 2: Starting CARLA agent..."
"$SCRIPT_DIR/start_carla_agent.sh" &
CARLA_PID=$!

echo ""
echo "System started!"
echo "DORA PID: $DORA_PID"
echo "CARLA Agent PID: $CARLA_PID"
echo ""
echo "Press Ctrl+C to stop all processes"

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping all processes..."
    kill $DORA_PID 2>/dev/null || true
    kill $CARLA_PID 2>/dev/null || true
    echo "Done."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait

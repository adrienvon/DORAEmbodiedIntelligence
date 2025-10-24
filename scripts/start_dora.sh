#!/bin/bash

# DORA Dataflow Launcher
# This script starts the DORA dataflow for autonomous driving

set -e

echo "=================================="
echo "CARLA-DORA Dataflow Launcher"
echo "=================================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
DATAFLOW_CONFIG="$PROJECT_ROOT/config/carla_dora_dataflow.yml"

echo "Project Root: $PROJECT_ROOT"
echo "Dataflow Config: $DATAFLOW_CONFIG"

# Check if DORA is installed
if ! command -v dora &> /dev/null; then
    echo "ERROR: dora command not found!"
    echo "Please install DORA first:"
    echo "  cargo install dora-cli"
    exit 1
fi

# Check if dataflow config exists
if [ ! -f "$DATAFLOW_CONFIG" ]; then
    echo "ERROR: Dataflow config not found: $DATAFLOW_CONFIG"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

echo ""
echo "Starting DORA dataflow..."
echo "Press Ctrl+C to stop"
echo ""

# Start DORA dataflow
dora start "$DATAFLOW_CONFIG" --attach

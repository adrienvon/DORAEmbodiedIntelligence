#!/bin/bash

# CARLA Leaderboard Launcher
# This script starts CARLA with our custom agent

set -e

echo "=================================="
echo "CARLA Leaderboard Launcher"
echo "=================================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# CARLA Leaderboard paths (UPDATE THESE!)
CARLA_ROOT="${CARLA_ROOT:-/path/to/carla}"
LEADERBOARD_ROOT="${LEADERBOARD_ROOT:-/path/to/leaderboard}"
SCENARIO_RUNNER_ROOT="${SCENARIO_RUNNER_ROOT:-/path/to/scenario_runner}"

# Configuration
ROUTES="${ROUTES:-$LEADERBOARD_ROOT/data/routes_training.xml}"
SCENARIOS="${SCENARIOS:-$LEADERBOARD_ROOT/data/all_towns_traffic_scenarios_public.json}"
AGENT="$PROJECT_ROOT/carla_agent/agent_wrapper.py"
AGENT_CONFIG="$PROJECT_ROOT/config/agent_config.json"
CHECKPOINT="${CHECKPOINT:-results/checkpoint.json}"
DEBUG=0

echo "Project Root: $PROJECT_ROOT"
echo "CARLA Root: $CARLA_ROOT"
echo "Leaderboard Root: $LEADERBOARD_ROOT"
echo "Agent: $AGENT"

# Check if CARLA is running
if ! nc -z localhost 2000 2>/dev/null; then
    echo "WARNING: CARLA server doesn't seem to be running on port 2000"
    echo "Please start CARLA server first:"
    echo "  cd $CARLA_ROOT && ./CarlaUE4.sh"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to abort..."
fi

# Set Python path
export PYTHONPATH="$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.14-py3.7-linux-x86_64.egg:$LEADERBOARD_ROOT:$SCENARIO_RUNNER_ROOT:$PROJECT_ROOT:$PYTHONPATH"

echo ""
echo "Starting CARLA Leaderboard..."
echo "Routes: $ROUTES"
echo "Agent: $AGENT"
echo ""

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Run leaderboard
python "$LEADERBOARD_ROOT/leaderboard/leaderboard_evaluator.py" \
    --routes="$ROUTES" \
    --scenarios="$SCENARIOS" \
    --agent="$AGENT" \
    --agent-config="$AGENT_CONFIG" \
    --checkpoint="$CHECKPOINT" \
    --debug=$DEBUG \
    --track=SENSORS

#!/bin/bash

# CARLA-DORA Complete System Launcher
# This is a convenience script that helps coordinate all three components

set -e

echo "========================================"
echo "CARLA-DORA System Launcher"
echo "========================================"
echo ""
echo "This script will help you start the complete system."
echo "You need to run components in 3 separate terminals."
echo ""
echo "========================================"
echo "TERMINAL SETUP GUIDE"
echo "========================================"
echo ""
echo "Terminal 1 - CARLA Server:"
echo "  cd \$CARLA_ROOT"
echo "  ./CarlaUE4.sh"
echo ""
echo "Terminal 2 - DORA Dataflow:"
echo "  cd $(pwd)"
echo "  ./scripts/start_dora.sh"
echo ""
echo "Terminal 3 - CARLA Agent:"
echo "  cd $(pwd)"
echo "  ./scripts/start_carla_agent.sh"
echo ""
echo "========================================"
echo "ENVIRONMENT CHECK"
echo "========================================"
echo ""

# Check CARLA_ROOT
if [ -z "$CARLA_ROOT" ]; then
    echo "⚠️  CARLA_ROOT not set!"
    echo "   Please set: export CARLA_ROOT=/path/to/carla"
else
    echo "✅ CARLA_ROOT: $CARLA_ROOT"
fi

# Check LEADERBOARD_ROOT
if [ -z "$LEADERBOARD_ROOT" ]; then
    echo "⚠️  LEADERBOARD_ROOT not set!"
    echo "   Please set: export LEADERBOARD_ROOT=/path/to/leaderboard"
else
    echo "✅ LEADERBOARD_ROOT: $LEADERBOARD_ROOT"
fi

# Check SCENARIO_RUNNER_ROOT
if [ -z "$SCENARIO_RUNNER_ROOT" ]; then
    echo "⚠️  SCENARIO_RUNNER_ROOT not set!"
    echo "   Please set: export SCENARIO_RUNNER_ROOT=/path/to/scenario_runner"
else
    echo "✅ SCENARIO_RUNNER_ROOT: $SCENARIO_RUNNER_ROOT"
fi

echo ""

# Check if CARLA is running
if nc -z localhost 2000 2>/dev/null; then
    echo "✅ CARLA server is running on port 2000"
else
    echo "⚠️  CARLA server is NOT running on port 2000"
    echo "   Start it in Terminal 1 first!"
fi

echo ""
echo "========================================"
echo "QUICK START COMMANDS"
echo "========================================"
echo ""
echo "If you just want to start DORA and Agent (assuming CARLA is running):"
echo ""
echo "# In one terminal:"
echo "./scripts/start_dora.sh"
echo ""
echo "# In another terminal:"
echo "./scripts/start_carla_agent.sh"
echo ""
echo "========================================"

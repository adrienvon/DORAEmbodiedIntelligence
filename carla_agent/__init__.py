"""
CARLA Agent Module
This module provides the bridge between CARLA Leaderboard and DORA platform.
"""

__version__ = "0.1.0"

# Import the entry point function for Leaderboard
from carla_agent.agent_wrapper import get_entry_point, CarlaDoraAgent

__all__ = ['get_entry_point', 'CarlaDoraAgent']

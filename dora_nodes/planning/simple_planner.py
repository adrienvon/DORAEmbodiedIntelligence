"""
Simple Planning Node
Implements basic autonomous driving logic based on GPS waypoints
"""

import pyarrow as pa
from dora import Node


class SimplePlanner:
    """Simple path planner using GPS waypoints"""
    
    def __init__(self):
        """Initialize the planner"""
        self.current_gps = None
        self.target_waypoints = []
        self.current_waypoint_idx = 0
        
        print("[SimplePlanner] Initialized")
    
    def update_gps(self, gps_data):
        """Update current GPS position"""
        self.current_gps = gps_data
    
    def plan(self):
        """
        Generate a simple driving plan
        
        Returns:
            Dictionary with target speed and steering direction
        """
        # Simple straight-line driving logic for initial testing
        # In a real scenario, this would compute path to waypoints
        
        plan = {
            'target_speed': 5.0,  # m/s (about 18 km/h)
            'target_steering': 0.0,  # Straight
            'waypoint_idx': self.current_waypoint_idx
        }
        
        return plan


def main():
    """Main entry point for DORA node"""
    
    # Initialize DORA node
    node = Node()
    
    # Initialize planner
    planner = SimplePlanner()
    
    print("[SimplePlanner] Node started")
    
    # Main event loop
    for event in node:
        if event["type"] == "INPUT":
            event_id = event["id"]
            
            # Update GPS data
            if event_id == "gps":
                gps_data = event["value"][0].as_py()
                planner.update_gps(gps_data)
                print(f"[SimplePlanner] GPS updated: {gps_data}")
            
            # When we receive speed data, generate a plan
            elif event_id == "speed":
                current_speed = event["value"][0].as_py()
                
                # Generate plan
                plan = planner.plan()
                
                # Send plan to control node
                node.send_output(
                    "plan",
                    pa.array([plan]),
                    event["metadata"]["timestamp"]
                )
                
                print(f"[SimplePlanner] Plan generated: speed={current_speed:.2f} m/s, "
                      f"target={plan['target_speed']:.2f} m/s")


if __name__ == "__main__":
    main()

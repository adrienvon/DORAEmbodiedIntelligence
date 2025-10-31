#!/usr/bin/env python3
"""
DORA Planner Operator - Pure Pursuit Path Tracking

This operator implements the core decision-making logic for autonomous driving.
It uses the Pure Pursuit algorithm to compute steering commands that follow
a predefined path based on the vehicle's current GNSS position.

Pure Pursuit Algorithm:
1. Determine vehicle's current position from GNSS
2. Find the lookahead point on the path (target waypoint)
3. Calculate the required steering angle to reach the lookahead point
4. Output control commands (steer, throttle, brake)

Author: DORA Autonomous Driving Team
Date: 2025-10-31
"""

import json
import math
from typing import Dict, List, Tuple, Optional, Any
import pyarrow as pa


# ============================================
# Configuration Constants
# ============================================

# Pure Pursuit Parameters
LOOKAHEAD_DISTANCE = 5.0  # meters - distance to look ahead on the path
MIN_LOOKAHEAD = 3.0       # meters - minimum lookahead distance
MAX_LOOKAHEAD = 10.0      # meters - maximum lookahead distance

# Control Parameters
CONSTANT_THROTTLE = 0.4   # Fixed throttle value for simple control
CONSTANT_BRAKE = 0.0      # No braking in this simple version

# Vehicle Parameters (CARLA default)
WHEELBASE = 2.89          # meters - distance between front and rear axles

# Path Following Tolerance
WAYPOINT_REACHED_THRESHOLD = 2.0  # meters - distance to consider waypoint reached


# ============================================
# Predefined Route (Example Waypoints)
# ============================================

# Simple rectangular test route in CARLA Town01 coordinates
# Format: List of (x, y) tuples in meters
DEFAULT_ROUTE: List[Tuple[float, float]] = [
    (0.0, 0.0),
    (50.0, 0.0),
    (50.0, 50.0),
    (0.0, 50.0),
    (0.0, 0.0),
]


# ============================================
# Utility Functions
# ============================================

def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two 2D points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
    
    Returns:
        Distance in meters
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx * dx + dy * dy)


def find_nearest_waypoint(position: Tuple[float, float], 
                          waypoints: List[Tuple[float, float]],
                          current_index: int) -> int:
    """
    Find the index of the nearest waypoint ahead of the vehicle.
    
    Args:
        position: Current vehicle position (x, y)
        waypoints: List of waypoints defining the path
        current_index: Current target waypoint index
    
    Returns:
        Index of the nearest waypoint ahead
    """
    min_distance = float('inf')
    nearest_index = current_index
    
    # Search forward from current index
    for i in range(current_index, len(waypoints)):
        distance = calculate_distance(position, waypoints[i])
        if distance < min_distance:
            min_distance = distance
            nearest_index = i
    
    return nearest_index


def find_lookahead_point(position: Tuple[float, float],
                         waypoints: List[Tuple[float, float]],
                         current_waypoint_index: int,
                         lookahead_distance: float) -> Tuple[Optional[Tuple[float, float]], int]:
    """
    Find the lookahead point on the path at the specified lookahead distance.
    
    Args:
        position: Current vehicle position (x, y)
        waypoints: List of waypoints defining the path
        current_waypoint_index: Current target waypoint index
        lookahead_distance: Desired lookahead distance in meters
    
    Returns:
        Tuple of (lookahead_point, next_waypoint_index) or (None, current_index) if not found
    """
    # Search from current waypoint to end of path
    for i in range(current_waypoint_index, len(waypoints)):
        waypoint = waypoints[i]
        distance = calculate_distance(position, waypoint)
        
        # If this waypoint is close to the lookahead distance, use it
        if distance >= lookahead_distance * 0.8:  # 80% threshold for flexibility
            return waypoint, i
    
    # If no suitable point found, use the last waypoint
    if len(waypoints) > 0:
        return waypoints[-1], len(waypoints) - 1
    
    return None, current_waypoint_index


def calculate_pure_pursuit_steering(vehicle_position: Tuple[float, float],
                                    vehicle_heading: float,
                                    target_point: Tuple[float, float],
                                    wheelbase: float) -> float:
    """
    Calculate steering angle using Pure Pursuit algorithm.
    
    The Pure Pursuit algorithm computes the curvature needed to reach
    a target point (lookahead point) from the vehicle's current position.
    
    Args:
        vehicle_position: Current vehicle position (x, y) in meters
        vehicle_heading: Current vehicle heading in radians (0 = East, π/2 = North)
        target_point: Target lookahead point (x, y) in meters
        wheelbase: Vehicle wheelbase in meters
    
    Returns:
        Steering angle in range [-1.0, 1.0] (CARLA convention)
    """
    # Calculate vector from vehicle to target
    dx = target_point[0] - vehicle_position[0]
    dy = target_point[1] - vehicle_position[1]
    
    # Calculate angle to target point in global frame
    target_angle = math.atan2(dy, dx)
    
    # Calculate heading error (difference between target angle and vehicle heading)
    alpha = target_angle - vehicle_heading
    
    # Normalize angle to [-π, π]
    alpha = math.atan2(math.sin(alpha), math.cos(alpha))
    
    # Calculate distance to target (lookahead distance)
    ld = math.sqrt(dx * dx + dy * dy)
    
    # Avoid division by zero
    if ld < 0.1:
        return 0.0
    
    # Pure Pursuit formula: steering angle = atan(2 * wheelbase * sin(alpha) / lookahead_distance)
    # Simplified: curvature = 2 * sin(alpha) / ld
    steering_angle = math.atan(2.0 * wheelbase * math.sin(alpha) / ld)
    
    # Convert to CARLA steering range [-1.0, 1.0]
    # Assuming max steering angle of ~30 degrees (0.52 radians)
    max_steering_rad = 0.52
    normalized_steering = steering_angle / max_steering_rad
    
    # Clamp to valid range
    normalized_steering = max(-1.0, min(1.0, normalized_steering))
    
    return normalized_steering


# ============================================
# DORA Operator Class
# ============================================

class Operator:
    """
    Pure Pursuit Planner Operator for DORA autonomous driving.
    
    This operator receives GNSS position data and computes steering commands
    to follow a predefined path using the Pure Pursuit algorithm.
    """
    
    def __init__(self):
        """
        Initialize the planner operator.
        
        Sets up the route waypoints and initializes state tracking variables.
        """
        print("=" * 60)
        print("PLANNER OPERATOR - Pure Pursuit Path Tracking")
        print("=" * 60)
        
        # Load predefined route
        self.waypoints: List[Tuple[float, float]] = DEFAULT_ROUTE.copy()
        print(f"[Planner] Loaded route with {len(self.waypoints)} waypoints")
        
        # State variables
        self.current_waypoint_index: int = 0
        self.vehicle_position: Optional[Tuple[float, float]] = None
        self.vehicle_heading: float = 0.0  # radians
        
        # Statistics
        self.total_commands_sent: int = 0
        self.path_completed: bool = False
        
        print(f"[Planner] Lookahead distance: {LOOKAHEAD_DISTANCE}m")
        print(f"[Planner] Constant throttle: {CONSTANT_THROTTLE}")
        print(f"[Planner] Wheelbase: {WHEELBASE}m")
        print("[Planner] Initialization complete")
        print("=" * 60)
    
    def on_event(
        self,
        dora_event: Dict[str, Any],
        send_output: Any,
    ) -> None:
        """
        Handle incoming DORA events (primarily GNSS data).
        
        This method is called by DORA whenever new data arrives on subscribed topics.
        It processes GNSS position data and computes control commands using Pure Pursuit.
        
        Args:
            dora_event: DORA event dictionary containing:
                - "type": Event type (e.g., "INPUT")
                - "id": Input topic ID (e.g., "gnss_data")
                - "value": PyArrow array containing the data
                - "metadata": Event metadata
            send_output: Callable to send data to DORA outputs
                Usage: send_output("output_id", pa_array, metadata)
        """
        event_type = dora_event["type"]
        
        # Only process INPUT events
        if event_type != "INPUT":
            return
        
        event_id = dora_event["id"]
        
        # Process GNSS data
        if event_id == "gnss_data":
            self._process_gnss_data(dora_event, send_output)
    
    def _process_gnss_data(self, dora_event: Dict[str, Any], send_output: Any) -> None:
        """
        Process incoming GNSS data and compute control commands.
        
        Args:
            dora_event: DORA event containing GNSS data
            send_output: Callable to send control commands
        """
        try:
            # Extract GNSS data from PyArrow array
            value = dora_event["value"]
            gnss_json_str = value[0].as_py()  # Get first element as Python object
            gnss_message = json.loads(gnss_json_str)
            
            # Extract position data
            gnss_data = gnss_message.get("data", {})
            latitude = gnss_data.get("latitude", 0.0)
            longitude = gnss_data.get("longitude", 0.0)
            altitude = gnss_data.get("altitude", 0.0)
            
            # For simplicity, treat lat/lon as x/y in a local coordinate frame
            # In a real system, you would convert GPS to a local coordinate system
            self.vehicle_position = (longitude, latitude)
            
            # Extract heading if available (otherwise use previous or default)
            # CARLA IMU data would provide orientation; for now, estimate from path
            if "heading" in gnss_data:
                self.vehicle_heading = math.radians(gnss_data["heading"])
            
            print(f"[Planner] Vehicle position: ({longitude:.2f}, {latitude:.2f}), "
                  f"altitude: {altitude:.2f}m")
            
            # Check if path is completed
            if self.path_completed:
                print("[Planner] Path completed - sending stop command")
                self._send_stop_command(send_output)
                return
            
            # Update current waypoint if close to target
            if self.current_waypoint_index < len(self.waypoints):
                current_waypoint = self.waypoints[self.current_waypoint_index]
                distance_to_waypoint = calculate_distance(self.vehicle_position, current_waypoint)
                
                if distance_to_waypoint < WAYPOINT_REACHED_THRESHOLD:
                    print(f"[Planner] Reached waypoint {self.current_waypoint_index}: {current_waypoint}")
                    self.current_waypoint_index += 1
                    
                    # Check if all waypoints reached
                    if self.current_waypoint_index >= len(self.waypoints):
                        print("[Planner] All waypoints reached! Path complete.")
                        self.path_completed = True
                        self._send_stop_command(send_output)
                        return
            
            # Find lookahead point using Pure Pursuit
            lookahead_point, next_index = find_lookahead_point(
                self.vehicle_position,
                self.waypoints,
                self.current_waypoint_index,
                LOOKAHEAD_DISTANCE
            )
            
            if lookahead_point is None:
                print("[Planner] Warning: No lookahead point found")
                self._send_stop_command(send_output)
                return
            
            # Estimate vehicle heading from movement direction if not available
            if self.current_waypoint_index > 0 and self.current_waypoint_index < len(self.waypoints):
                prev_wp = self.waypoints[self.current_waypoint_index - 1]
                curr_wp = self.waypoints[self.current_waypoint_index]
                dx = curr_wp[0] - prev_wp[0]
                dy = curr_wp[1] - prev_wp[1]
                self.vehicle_heading = math.atan2(dy, dx)
            
            # Calculate steering using Pure Pursuit
            steering = calculate_pure_pursuit_steering(
                self.vehicle_position,
                self.vehicle_heading,
                lookahead_point,
                WHEELBASE
            )
            
            # Create control command
            control_command = {
                "steer": float(steering),
                "throttle": float(CONSTANT_THROTTLE),
                "brake": float(CONSTANT_BRAKE),
                "timestamp": gnss_message.get("timestamp", 0.0)
            }
            
            # Send control command to DORA
            control_json = json.dumps(control_command)
            send_output("control_cmd", pa.array([control_json]))
            
            self.total_commands_sent += 1
            
            print(f"[Planner] Control command #{self.total_commands_sent}: "
                  f"steer={steering:.3f}, throttle={CONSTANT_THROTTLE:.2f}, "
                  f"target=({lookahead_point[0]:.2f}, {lookahead_point[1]:.2f})")
        
        except Exception as e:
            print(f"[Planner] Error processing GNSS data: {e}")
            import traceback
            traceback.print_exc()
    
    def _send_stop_command(self, send_output: Any) -> None:
        """
        Send a stop command (zero throttle, full brake).
        
        Args:
            send_output: Callable to send control commands
        """
        stop_command = {
            "steer": 0.0,
            "throttle": 0.0,
            "brake": 1.0,
            "timestamp": 0.0
        }
        
        stop_json = json.dumps(stop_command)
        send_output("control_cmd", pa.array([stop_json]))
        print("[Planner] Stop command sent")

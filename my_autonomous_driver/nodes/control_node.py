#!/usr/bin/env python3
"""
DORA Control Sender Node - DORA to CARLA Bridge

This node acts as the output gateway from the DORA dataflow back to the CARLA simulator.
It receives control commands (steer, throttle, brake) from the planner operator and sends
them to the CARLA agent via UDP network socket.

Architecture:
- Main thread: DORA event loop listening for control commands
- UDP client: Sends control commands to CARLA agent

Author: DORA Autonomous Driving Team
Date: 2025-10-31
"""

import json
import socket
import time
from typing import Dict, Any, Optional
import pyarrow as pa
from dora import Node


# ============================================
# Configuration Constants
# ============================================

# CARLA Agent Network Configuration
CARLA_AGENT_HOST = "192.168.1.1"  # IP address of CARLA agent
CARLA_AGENT_PORT = 23456          # Port where CARLA agent listens

# Socket Configuration
SOCKET_TIMEOUT = 1.0              # seconds - timeout for socket operations
SEND_RETRY_ATTEMPTS = 3           # number of retry attempts for failed sends
RETRY_DELAY = 0.1                 # seconds - delay between retry attempts

# Control Command Validation
MIN_STEER = -1.0                  # minimum steering value
MAX_STEER = 1.0                   # maximum steering value
MIN_THROTTLE = 0.0                # minimum throttle value
MAX_THROTTLE = 1.0                # maximum throttle value
MIN_BRAKE = 0.0                   # minimum brake value
MAX_BRAKE = 1.0                   # maximum brake value


# ============================================
# Utility Functions
# ============================================

def validate_control_command(control: Dict[str, Any]) -> bool:
    """
    Validate control command values are within acceptable ranges.
    
    Args:
        control: Dictionary containing steer, throttle, brake values
    
    Returns:
        True if valid, False otherwise
    """
    try:
        steer = control.get("steer", 0.0)
        throttle = control.get("throttle", 0.0)
        brake = control.get("brake", 0.0)
        
        # Check if values are within valid ranges
        if not (MIN_STEER <= steer <= MAX_STEER):
            print(f"[Control] Warning: Invalid steer value {steer}, expected [{MIN_STEER}, {MAX_STEER}]")
            return False
        
        if not (MIN_THROTTLE <= throttle <= MAX_THROTTLE):
            print(f"[Control] Warning: Invalid throttle value {throttle}, expected [{MIN_THROTTLE}, {MAX_THROTTLE}]")
            return False
        
        if not (MIN_BRAKE <= brake <= MAX_BRAKE):
            print(f"[Control] Warning: Invalid brake value {brake}, expected [{MIN_BRAKE}, {MAX_BRAKE}]")
            return False
        
        return True
    
    except Exception as e:
        print(f"[Control] Error validating control command: {e}")
        return False


def clamp_control_command(control: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clamp control command values to valid ranges.
    
    Args:
        control: Dictionary containing steer, throttle, brake values
    
    Returns:
        Dictionary with clamped values
    """
    clamped = control.copy()
    
    # Clamp steering
    if "steer" in clamped:
        clamped["steer"] = max(MIN_STEER, min(MAX_STEER, clamped["steer"]))
    
    # Clamp throttle
    if "throttle" in clamped:
        clamped["throttle"] = max(MIN_THROTTLE, min(MAX_THROTTLE, clamped["throttle"]))
    
    # Clamp brake
    if "brake" in clamped:
        clamped["brake"] = max(MIN_BRAKE, min(MAX_BRAKE, clamped["brake"]))
    
    return clamped


# ============================================
# UDP Control Sender Class
# ============================================

class UDPControlSender:
    """
    UDP client for sending control commands to CARLA agent.
    
    This class manages the UDP socket connection and handles sending
    control commands with retry logic and error handling.
    """
    
    def __init__(self, host: str, port: int):
        """
        Initialize UDP control sender.
        
        Args:
            host: CARLA agent IP address
            port: CARLA agent port number
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.commands_sent = 0
        self.send_failures = 0
        
        self._create_socket()
    
    def _create_socket(self) -> None:
        """Create and configure UDP socket."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(SOCKET_TIMEOUT)
            print(f"[Control] UDP socket created for {self.host}:{self.port}")
        except Exception as e:
            print(f"[Control] Error creating UDP socket: {e}")
            self.socket = None
    
    def send_control_command(self, control: Dict[str, Any]) -> bool:
        """
        Send control command to CARLA agent via UDP.
        
        Args:
            control: Dictionary containing steer, throttle, brake values
        
        Returns:
            True if successfully sent, False otherwise
        """
        if self.socket is None:
            print("[Control] Socket not initialized, attempting to recreate...")
            self._create_socket()
            if self.socket is None:
                return False
        
        # Validate and clamp control values
        if not validate_control_command(control):
            print("[Control] Clamping invalid control values...")
            control = clamp_control_command(control)
        
        # Serialize control command to JSON
        try:
            control_json = json.dumps(control)
            control_bytes = control_json.encode('utf-8')
        except Exception as e:
            print(f"[Control] Error serializing control command: {e}")
            return False
        
        # Send with retry logic
        for attempt in range(SEND_RETRY_ATTEMPTS):
            try:
                bytes_sent = self.socket.sendto(control_bytes, (self.host, self.port))
                
                if bytes_sent == len(control_bytes):
                    self.commands_sent += 1
                    return True
                else:
                    print(f"[Control] Partial send: {bytes_sent}/{len(control_bytes)} bytes")
            
            except socket.timeout:
                print(f"[Control] Send timeout (attempt {attempt + 1}/{SEND_RETRY_ATTEMPTS})")
            except socket.error as e:
                print(f"[Control] Socket error (attempt {attempt + 1}/{SEND_RETRY_ATTEMPTS}): {e}")
            except Exception as e:
                print(f"[Control] Unexpected error (attempt {attempt + 1}/{SEND_RETRY_ATTEMPTS}): {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < SEND_RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
        
        # All retry attempts failed
        self.send_failures += 1
        print(f"[Control] Failed to send command after {SEND_RETRY_ATTEMPTS} attempts")
        return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get sending statistics.
        
        Returns:
            Dictionary with commands_sent and send_failures counts
        """
        return {
            "commands_sent": self.commands_sent,
            "send_failures": self.send_failures
        }
    
    def close(self) -> None:
        """Close the UDP socket."""
        if self.socket is not None:
            try:
                self.socket.close()
                print("[Control] UDP socket closed")
            except Exception as e:
                print(f"[Control] Error closing socket: {e}")
            finally:
                self.socket = None


# ============================================
# Main DORA Node
# ============================================

def main():
    """
    Main DORA node entry point.
    
    This function:
    1. Initializes the UDP control sender
    2. Enters the DORA event loop
    3. Listens for control commands from the planner
    4. Sends control commands to CARLA agent via UDP
    """
    print("=" * 60)
    print("DORA CONTROL SENDER NODE - DORA to CARLA Bridge")
    print("=" * 60)
    
    # Initialize UDP control sender
    control_sender = UDPControlSender(CARLA_AGENT_HOST, CARLA_AGENT_PORT)
    print(f"[Control] Sending commands to CARLA agent at {CARLA_AGENT_HOST}:{CARLA_AGENT_PORT}")
    
    # Initialize DORA node
    node = Node()
    print("[Control] DORA node initialized")
    print("[Control] Waiting for control commands from planner...")
    print("=" * 60)
    
    # Statistics
    last_stats_time = time.time()
    stats_interval = 10.0  # seconds - print statistics every 10 seconds
    
    # DORA event loop
    try:
        for event in node:
            event_type = event["type"]
            
            # Process INPUT events (control commands)
            if event_type == "INPUT":
                event_id = event["id"]
                
                # Handle control command input
                if event_id == "control_cmd":
                    try:
                        # Extract control command from PyArrow array
                        value = event["value"]
                        control_json_str = value[0].as_py()  # Get first element as Python object
                        control_command = json.loads(control_json_str)
                        
                        # Extract control values
                        steer = control_command.get("steer", 0.0)
                        throttle = control_command.get("throttle", 0.0)
                        brake = control_command.get("brake", 0.0)
                        timestamp = control_command.get("timestamp", 0.0)
                        
                        print(f"[Control] Received command: steer={steer:.3f}, "
                              f"throttle={throttle:.3f}, brake={brake:.3f}, "
                              f"timestamp={timestamp:.3f}")
                        
                        # Send control command to CARLA
                        success = control_sender.send_control_command(control_command)
                        
                        if success:
                            print(f"[Control] ✓ Command sent to CARLA successfully")
                        else:
                            print(f"[Control] ✗ Failed to send command to CARLA")
                    
                    except json.JSONDecodeError as e:
                        print(f"[Control] Error: Invalid JSON in control command: {e}")
                    except Exception as e:
                        print(f"[Control] Error processing control command: {e}")
                        import traceback
                        traceback.print_exc()
                
                else:
                    print(f"[Control] Received unexpected input: {event_id}")
            
            # Print statistics periodically
            current_time = time.time()
            if current_time - last_stats_time >= stats_interval:
                stats = control_sender.get_statistics()
                print(f"[Control] Statistics - Sent: {stats['commands_sent']}, "
                      f"Failed: {stats['send_failures']}")
                last_stats_time = current_time
    
    except KeyboardInterrupt:
        print("\n[Control] Shutting down control sender node...")
    except Exception as e:
        print(f"[Control] Fatal error in DORA event loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        control_sender.close()
        print("[Control] Node shutdown complete")


# ============================================
# Entry Point
# ============================================

if __name__ == "__main__":
    main()

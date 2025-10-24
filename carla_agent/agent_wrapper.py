"""
CARLA Agent Wrapper
This script acts as a bridge between CARLA Leaderboard and DORA platform.
It receives sensor data from CARLA, sends it to DORA via UDP, and receives
control commands from DORA to control the vehicle.
"""

import socket
import time
import msgpack
import numpy as np
from typing import Dict, Any, Optional


class DoraUDPBridge:
    """UDP Communication Bridge between CARLA and DORA"""
    
    def __init__(self, 
                 carla_to_dora_port: int = 8001,
                 dora_to_carla_port: int = 8002,
                 host: str = 'localhost',
                 timeout: float = 0.01):
        """
        Initialize UDP bridge
        
        Args:
            carla_to_dora_port: Port to send data from CARLA to DORA
            dora_to_carla_port: Port to receive control commands from DORA
            host: Host address
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.carla_to_dora_port = carla_to_dora_port
        self.dora_to_carla_port = dora_to_carla_port
        
        # Socket for sending sensor data to DORA
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Socket for receiving control commands from DORA
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.settimeout(timeout)
        self.recv_socket.bind((host, dora_to_carla_port))
        
        print(f"[DoraUDPBridge] Initialized:")
        print(f"  - Sending sensor data to {host}:{carla_to_dora_port}")
        print(f"  - Receiving control from {host}:{dora_to_carla_port}")
    
    def send_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """
        Send sensor data to DORA
        
        Args:
            sensor_data: Dictionary containing sensor readings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize data using msgpack
            packed_data = msgpack.packb(sensor_data, use_bin_type=True)
            
            # Send via UDP
            self.send_socket.sendto(
                packed_data, 
                (self.host, self.carla_to_dora_port)
            )
            return True
        except Exception as e:
            print(f"[DoraUDPBridge] Error sending sensor data: {e}")
            return False
    
    def receive_control(self) -> Optional[Dict[str, float]]:
        """
        Receive control commands from DORA
        
        Returns:
            Dictionary with control commands or None if no data
        """
        try:
            data, addr = self.recv_socket.recvfrom(4096)
            control = msgpack.unpackb(data, raw=False)
            return control
        except socket.timeout:
            return None
        except Exception as e:
            print(f"[DoraUDPBridge] Error receiving control: {e}")
            return None
    
    def close(self):
        """Close all sockets"""
        self.send_socket.close()
        self.recv_socket.close()


class CarlaDoraAgent:
    """
    CARLA Agent that integrates with DORA platform
    This agent follows the CARLA Leaderboard API
    """
    
    def __init__(self):
        """Initialize the agent"""
        self.bridge = None
        self.step_count = 0
        print("[CarlaDoraAgent] Agent initialized")
    
    def setup(self, path_to_conf_file: str):
        """
        Setup the agent with configuration file
        
        Args:
            path_to_conf_file: Path to configuration file
        """
        print(f"[CarlaDoraAgent] Setup with config: {path_to_conf_file}")
        
        # Initialize UDP bridge
        self.bridge = DoraUDPBridge()
        
    def sensors(self) -> list:
        """
        Define the sensor suite required by the agent
        
        Returns:
            List of sensor specifications
        """
        sensors = [
            # GPS sensor
            {
                'type': 'sensor.other.gnss',
                'x': 0.0, 'y': 0.0, 'z': 0.0,
                'id': 'GPS'
            },
            # IMU sensor
            {
                'type': 'sensor.other.imu',
                'x': 0.0, 'y': 0.0, 'z': 0.0,
                'id': 'IMU'
            },
            # Speedometer
            {
                'type': 'sensor.speedometer',
                'reading_frequency': 20,
                'id': 'Speed'
            },
            # Front camera
            {
                'type': 'sensor.camera.rgb',
                'x': 2.0, 'y': 0.0, 'z': 1.4,
                'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
                'width': 800, 'height': 600, 'fov': 100,
                'id': 'Center'
            },
        ]
        
        return sensors
    
    def run_step(self, input_data: Dict, timestamp: float) -> Dict[str, float]:
        """
        Execute one step of navigation
        
        Args:
            input_data: Dictionary of sensor data
            timestamp: Current timestamp
            
        Returns:
            Dictionary with control commands (throttle, steer, brake)
        """
        self.step_count += 1
        
        # Extract and package sensor data
        sensor_data = self._extract_sensor_data(input_data)
        sensor_data['timestamp'] = timestamp
        sensor_data['step'] = self.step_count
        
        # Send sensor data to DORA
        if self.bridge:
            self.bridge.send_sensor_data(sensor_data)
            
            # Receive control command from DORA
            control = self.bridge.receive_control()
            
            if control:
                return control
        
        # Default control (fallback)
        return {
            'throttle': 0.0,
            'steer': 0.0,
            'brake': 1.0
        }
    
    def _extract_sensor_data(self, input_data: Dict) -> Dict[str, Any]:
        """
        Extract and format sensor data
        
        Args:
            input_data: Raw input data from CARLA
            
        Returns:
            Formatted sensor data dictionary
        """
        sensor_data = {}
        
        # Extract GPS data
        if 'GPS' in input_data:
            gps = input_data['GPS'][1]
            sensor_data['gps'] = {
                'latitude': float(gps[0]) if hasattr(gps, '__getitem__') else 0.0,
                'longitude': float(gps[1]) if hasattr(gps, '__getitem__') else 0.0,
                'altitude': float(gps[2]) if len(gps) > 2 else 0.0
            }
        
        # Extract IMU data
        if 'IMU' in input_data:
            imu = input_data['IMU'][1]
            sensor_data['imu'] = {
                'accelerometer': [float(x) for x in getattr(imu, 'accelerometer', [0, 0, 0])],
                'gyroscope': [float(x) for x in getattr(imu, 'gyroscope', [0, 0, 0])],
                'compass': float(getattr(imu, 'compass', 0.0))
            }
        
        # Extract speed data
        if 'Speed' in input_data:
            speed = input_data['Speed'][1]
            sensor_data['speed'] = float(speed['speed']) if isinstance(speed, dict) else float(speed)
        
        # Extract camera data (only metadata to reduce bandwidth)
        if 'Center' in input_data:
            camera = input_data['Center'][1]
            sensor_data['camera'] = {
                'width': camera.shape[1] if hasattr(camera, 'shape') else 800,
                'height': camera.shape[0] if hasattr(camera, 'shape') else 600,
                'channels': camera.shape[2] if hasattr(camera, 'shape') and len(camera.shape) > 2 else 3
            }
            # Note: We don't send the full image data via UDP due to size constraints
            # In production, consider using a separate image streaming solution
        
        return sensor_data
    
    def destroy(self):
        """Cleanup resources"""
        if self.bridge:
            self.bridge.close()
        print("[CarlaDoraAgent] Agent destroyed")


# Entry point for CARLA Leaderboard
def get_entry_point():
    """Return the agent class for CARLA Leaderboard"""
    return 'CarlaDoraAgent'

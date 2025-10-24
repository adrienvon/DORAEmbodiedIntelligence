"""
Sensor Receiver Node
Receives sensor data from CARLA via UDP and publishes to DORA dataflow
"""

import socket
import msgpack
import pyarrow as pa
from dora import Node


class SensorReceiver:
    """Receives sensor data from CARLA via UDP"""
    
    def __init__(self, port: int = 8001, host: str = 'localhost'):
        """
        Initialize sensor receiver
        
        Args:
            port: UDP port to listen on
            host: Host address to bind to
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.socket.settimeout(0.01)
        
        print(f"[SensorReceiver] Listening on {host}:{port}")
    
    def receive(self):
        """
        Receive sensor data from UDP socket
        
        Returns:
            Sensor data dictionary or None
        """
        try:
            data, addr = self.socket.recvfrom(65535)
            sensor_data = msgpack.unpackb(data, raw=False)
            return sensor_data
        except socket.timeout:
            return None
        except Exception as e:
            print(f"[SensorReceiver] Error: {e}")
            return None
    
    def close(self):
        """Close the socket"""
        self.socket.close()


def main():
    """Main entry point for DORA node"""
    
    # Initialize DORA node
    node = Node()
    
    # Initialize sensor receiver
    receiver = SensorReceiver()
    
    print("[SensorReceiver] Node started")
    
    try:
        # Main event loop
        for event in node:
            if event["type"] == "INPUT":
                # Handle incoming DORA events (if any)
                pass
            
            # Continuously receive sensor data
            sensor_data = receiver.receive()
            
            if sensor_data:
                # Send GPS data
                if 'gps' in sensor_data:
                    node.send_output(
                        "gps",
                        pa.array([sensor_data['gps']]),
                        sensor_data.get('timestamp', 0)
                    )
                
                # Send IMU data
                if 'imu' in sensor_data:
                    node.send_output(
                        "imu",
                        pa.array([sensor_data['imu']]),
                        sensor_data.get('timestamp', 0)
                    )
                
                # Send speed data
                if 'speed' in sensor_data:
                    node.send_output(
                        "speed",
                        pa.array([sensor_data['speed']]),
                        sensor_data.get('timestamp', 0)
                    )
                
                # Send camera metadata
                if 'camera' in sensor_data:
                    node.send_output(
                        "camera_info",
                        pa.array([sensor_data['camera']]),
                        sensor_data.get('timestamp', 0)
                    )
                
                print(f"[SensorReceiver] Received data at step {sensor_data.get('step', 0)}")
    
    finally:
        receiver.close()
        print("[SensorReceiver] Node stopped")


if __name__ == "__main__":
    main()

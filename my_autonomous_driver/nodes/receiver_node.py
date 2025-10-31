#!/usr/bin/env python3
"""
DORA Receiver Node - CARLA to DORA Bridge

This node acts as the input gateway from the CARLA simulator into the DORA dataflow.
It receives sensor data (GNSS, IMU, LiDAR) from CARLA via network sockets and publishes
them as DORA outputs for downstream processing.

Architecture:
- Main thread: DORA event loop
- UDP Server thread: Receives GNSS and IMU data (JSON format) on port 12345
- TCP Server thread: Receives LiDAR data (binary format) on port 5005

Author: DORA Autonomous Driving Team
Date: 2025-10-31
"""

import json
import socket
import struct
import threading
import time
from typing import Dict, Any, Optional
import pyarrow as pa
from dora import Node

# ============================================
# Configuration Constants
# ============================================

UDP_HOST = "0.0.0.0"  # Listen on all network interfaces
UDP_PORT = 12345      # Port for GNSS and IMU data (JSON)

TCP_HOST = "0.0.0.0"  # Listen on all network interfaces
TCP_PORT = 5005       # Port for LiDAR data (binary)

BUFFER_SIZE = 65536   # 64KB buffer for UDP packets
LIDAR_BUFFER_SIZE = 1024 * 1024  # 1MB buffer for LiDAR data


# ============================================
# Global Data Storage (Thread-Safe)
# ============================================

class SensorDataBuffer:
    """Thread-safe buffer for storing incoming sensor data."""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.gnss_data: Optional[Dict[str, Any]] = None
        self.imu_data: Optional[Dict[str, Any]] = None
        self.lidar_data: Optional[bytes] = None
        self.gnss_updated = False
        self.imu_updated = False
        self.lidar_updated = False
    
    def set_gnss(self, data: Dict[str, Any]) -> None:
        """Store GNSS data and mark as updated."""
        with self.lock:
            self.gnss_data = data
            self.gnss_updated = True
    
    def set_imu(self, data: Dict[str, Any]) -> None:
        """Store IMU data and mark as updated."""
        with self.lock:
            self.imu_data = data
            self.imu_updated = True
    
    def set_lidar(self, data: bytes) -> None:
        """Store LiDAR data and mark as updated."""
        with self.lock:
            self.lidar_data = data
            self.lidar_updated = True
    
    def get_and_clear_gnss(self) -> Optional[Dict[str, Any]]:
        """Retrieve GNSS data if updated, then clear the flag."""
        with self.lock:
            if self.gnss_updated:
                data = self.gnss_data
                self.gnss_updated = False
                return data
            return None
    
    def get_and_clear_imu(self) -> Optional[Dict[str, Any]]:
        """Retrieve IMU data if updated, then clear the flag."""
        with self.lock:
            if self.imu_updated:
                data = self.imu_data
                self.imu_updated = False
                return data
            return None
    
    def get_and_clear_lidar(self) -> Optional[bytes]:
        """Retrieve LiDAR data if updated, then clear the flag."""
        with self.lock:
            if self.lidar_updated:
                data = self.lidar_data
                self.lidar_updated = False
                return data
            return None


# Global sensor buffer instance
sensor_buffer = SensorDataBuffer()


# ============================================
# UDP Server for GNSS and IMU Data
# ============================================

def udp_server_thread():
    """
    UDP server thread that receives GNSS and IMU data from CARLA.
    
    Expected JSON format from CARLA:
    {
        "type": "gnss" | "imu",
        "timestamp": float,
        "data": { ... sensor-specific fields ... }
    }
    """
    print(f"[UDP Server] Starting on {UDP_HOST}:{UDP_PORT}")
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((UDP_HOST, UDP_PORT))
        print(f"[UDP Server] Listening for GNSS/IMU data...")
        
        while True:
            try:
                # Receive data from CARLA
                data, addr = sock.recvfrom(BUFFER_SIZE)
                
                # Parse JSON data
                try:
                    message = json.loads(data.decode('utf-8'))
                    sensor_type = message.get("type", "unknown")
                    
                    if sensor_type == "gnss":
                        sensor_buffer.set_gnss(message)
                        print(f"[UDP Server] Received GNSS data from {addr}")
                    
                    elif sensor_type == "imu":
                        sensor_buffer.set_imu(message)
                        print(f"[UDP Server] Received IMU data from {addr}")
                    
                    else:
                        print(f"[UDP Server] Unknown sensor type: {sensor_type}")
                
                except json.JSONDecodeError as e:
                    print(f"[UDP Server] JSON decode error: {e}")
                except Exception as e:
                    print(f"[UDP Server] Error processing message: {e}")
            
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[UDP Server] Socket error: {e}")
                time.sleep(1)  # Brief pause before retry
    
    except Exception as e:
        print(f"[UDP Server] Fatal error: {e}")
    finally:
        sock.close()
        print("[UDP Server] Shutdown")


# ============================================
# TCP Server for LiDAR Data
# ============================================

def handle_lidar_client(client_socket: socket.socket, addr: tuple):
    """
    Handle individual LiDAR client connection.
    
    Expected binary format:
    - 4 bytes: message length (uint32, big-endian)
    - N bytes: LiDAR point cloud data
    """
    print(f"[TCP Server] Client connected from {addr}")
    
    try:
        while True:
            # Read message length header (4 bytes)
            length_data = client_socket.recv(4)
            if not length_data or len(length_data) < 4:
                print(f"[TCP Server] Client {addr} disconnected")
                break
            
            # Unpack message length
            message_length = struct.unpack('>I', length_data)[0]
            
            # Read the full message
            received_data = b''
            remaining = message_length
            
            while remaining > 0:
                chunk = client_socket.recv(min(remaining, LIDAR_BUFFER_SIZE))
                if not chunk:
                    print(f"[TCP Server] Connection lost from {addr}")
                    return
                received_data += chunk
                remaining -= len(chunk)
            
            # Store LiDAR data in buffer
            sensor_buffer.set_lidar(received_data)
            print(f"[TCP Server] Received LiDAR data ({len(received_data)} bytes) from {addr}")
    
    except Exception as e:
        print(f"[TCP Server] Error handling client {addr}: {e}")
    finally:
        client_socket.close()
        print(f"[TCP Server] Connection closed: {addr}")


def tcp_server_thread():
    """
    TCP server thread that accepts LiDAR data connections from CARLA.
    Each client connection is handled in a separate thread.
    """
    print(f"[TCP Server] Starting on {TCP_HOST}:{TCP_PORT}")
    
    # Create TCP socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_sock.bind((TCP_HOST, TCP_PORT))
        server_sock.listen(5)  # Allow up to 5 queued connections
        print(f"[TCP Server] Listening for LiDAR data...")
        
        while True:
            try:
                # Accept incoming client connection
                client_socket, addr = server_sock.accept()
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=handle_lidar_client,
                    args=(client_socket, addr),
                    daemon=True
                )
                client_thread.start()
            
            except Exception as e:
                print(f"[TCP Server] Error accepting connection: {e}")
                time.sleep(1)
    
    except Exception as e:
        print(f"[TCP Server] Fatal error: {e}")
    finally:
        server_sock.close()
        print("[TCP Server] Shutdown")


# ============================================
# Main DORA Node
# ============================================

def main():
    """
    Main DORA node entry point.
    
    This function:
    1. Starts UDP and TCP server threads
    2. Enters the DORA event loop
    3. Publishes sensor data to DORA outputs when available
    """
    print("=" * 60)
    print("DORA RECEIVER NODE - CARLA to DORA Bridge")
    print("=" * 60)
    
    # Start UDP server thread for GNSS and IMU
    udp_thread = threading.Thread(target=udp_server_thread, daemon=True)
    udp_thread.start()
    print("[Main] UDP server thread started")
    
    # Start TCP server thread for LiDAR
    tcp_thread = threading.Thread(target=tcp_server_thread, daemon=True)
    tcp_thread.start()
    print("[Main] TCP server thread started")
    
    # Brief pause to allow servers to initialize
    time.sleep(0.5)
    
    # Initialize DORA node
    node = Node()
    print("[Main] DORA node initialized")
    print("[Main] Waiting for sensor data from CARLA...")
    print("=" * 60)
    
    # DORA event loop
    try:
        for event in node:
            event_type = event["type"]
            
            # Handle timer ticks or other input events
            if event_type == "INPUT":
                event_id = event["id"]
                print(f"[Main] Received DORA input: {event_id}")
            
            # Check for new GNSS data
            gnss_data = sensor_buffer.get_and_clear_gnss()
            if gnss_data is not None:
                # Convert to PyArrow format and send to DORA
                gnss_json = json.dumps(gnss_data)
                node.send_output("gnss_data", pa.array([gnss_json]))
                print(f"[Main] Published GNSS data to DORA: timestamp={gnss_data.get('timestamp', 'N/A')}")
            
            # Check for new IMU data
            imu_data = sensor_buffer.get_and_clear_imu()
            if imu_data is not None:
                # Convert to PyArrow format and send to DORA
                imu_json = json.dumps(imu_data)
                node.send_output("imu_data", pa.array([imu_json]))
                print(f"[Main] Published IMU data to DORA: timestamp={imu_data.get('timestamp', 'N/A')}")
            
            # Check for new LiDAR data
            lidar_data = sensor_buffer.get_and_clear_lidar()
            if lidar_data is not None:
                # Send binary data as PyArrow binary array
                node.send_output("lidar_data", pa.array([lidar_data], type=pa.binary()))
                print(f"[Main] Published LiDAR data to DORA: {len(lidar_data)} bytes")
            
            # Small sleep to prevent busy-waiting
            time.sleep(0.01)  # 10ms polling interval
    
    except KeyboardInterrupt:
        print("\n[Main] Shutting down receiver node...")
    except Exception as e:
        print(f"[Main] Error in DORA event loop: {e}")
        raise


# ============================================
# Entry Point
# ============================================

if __name__ == "__main__":
    main()

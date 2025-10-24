#!/usr/bin/env python3
"""
UDP Communication Test Script
Tests the UDP bridge between CARLA and DORA without requiring full setup
"""

import socket
import time
import msgpack
import sys


def test_sensor_sender():
    """Simulate CARLA sending sensor data"""
    print("=== Testing Sensor Data Sender ===")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    target = ('localhost', 8001)
    
    print(f"Sending sensor data to {target}")
    
    for i in range(5):
        sensor_data = {
            'step': i,
            'timestamp': time.time(),
            'gps': {
                'latitude': 48.858 + i * 0.001,
                'longitude': 2.294 + i * 0.001,
                'altitude': 35.0
            },
            'imu': {
                'accelerometer': [0.1, 0.2, 9.8],
                'gyroscope': [0.01, 0.02, 0.03],
                'compass': 45.0
            },
            'speed': 10.0 + i * 2.0,
            'camera': {
                'width': 800,
                'height': 600,
                'channels': 3
            }
        }
        
        packed = msgpack.packb(sensor_data, use_bin_type=True)
        sock.sendto(packed, target)
        
        print(f"  [Step {i}] Sent sensor data: speed={sensor_data['speed']:.1f} m/s")
        time.sleep(0.5)
    
    sock.close()
    print("✓ Sensor sender test completed\n")


def test_control_receiver():
    """Simulate CARLA receiving control commands"""
    print("=== Testing Control Receiver ===")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 8002))
    sock.settimeout(5.0)
    
    print("Listening for control commands on port 8002")
    print("Waiting for 5 seconds...")
    
    received_count = 0
    
    try:
        while received_count < 3:
            data, addr = sock.recvfrom(4096)
            control = msgpack.unpackb(data, raw=False)
            
            print(f"  Received control from {addr}:")
            print(f"    throttle: {control.get('throttle', 0):.2f}")
            print(f"    steer: {control.get('steer', 0):.2f}")
            print(f"    brake: {control.get('brake', 0):.2f}")
            
            received_count += 1
    
    except socket.timeout:
        if received_count == 0:
            print("  ⚠ No control commands received (timeout)")
        else:
            print(f"  ✓ Received {received_count} control commands")
    
    sock.close()
    print("✓ Control receiver test completed\n")


def test_control_sender():
    """Simulate DORA sending control commands"""
    print("=== Testing Control Sender ===")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    target = ('localhost', 8002)
    
    print(f"Sending control commands to {target}")
    
    controls = [
        {'throttle': 0.5, 'steer': 0.0, 'brake': 0.0},  # Accelerate
        {'throttle': 0.3, 'steer': -0.2, 'brake': 0.0},  # Turn left
        {'throttle': 0.0, 'steer': 0.0, 'brake': 0.8},  # Brake
    ]
    
    for i, control in enumerate(controls):
        packed = msgpack.packb(control, use_bin_type=True)
        sock.sendto(packed, target)
        
        print(f"  [Command {i+1}] Sent: throttle={control['throttle']:.2f}, "
              f"steer={control['steer']:.2f}, brake={control['brake']:.2f}")
        time.sleep(0.5)
    
    sock.close()
    print("✓ Control sender test completed\n")


def test_bidirectional():
    """Test bidirectional communication"""
    print("=== Testing Bidirectional Communication ===")
    print("This simulates the full CARLA <-> DORA loop\n")
    
    # Create sockets
    sensor_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_recv_sock.bind(('localhost', 8002))
    control_recv_sock.settimeout(0.1)
    
    control_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print("Starting 3-step simulation:")
    
    for i in range(3):
        # 1. Send sensor data (CARLA -> DORA)
        sensor_data = {
            'step': i,
            'timestamp': time.time(),
            'speed': 5.0 + i * 3.0,
            'gps': {'latitude': 48.858, 'longitude': 2.294}
        }
        
        packed = msgpack.packb(sensor_data, use_bin_type=True)
        sensor_sock.sendto(packed, ('localhost', 8001))
        print(f"  Step {i+1}: Sent sensor (speed={sensor_data['speed']:.1f})")
        
        time.sleep(0.2)
        
        # 2. Receive control command (DORA -> CARLA)
        try:
            data, addr = control_recv_sock.recvfrom(4096)
            control = msgpack.unpackb(data, raw=False)
            print(f"         Received control (throttle={control.get('throttle', 0):.2f})")
        except socket.timeout:
            print(f"         (No control received)")
        
        time.sleep(0.3)
    
    # Cleanup
    sensor_sock.close()
    control_recv_sock.close()
    control_send_sock.close()
    
    print("\n✓ Bidirectional test completed\n")


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("  CARLA-DORA UDP Communication Test")
    print("="*60 + "\n")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == 'sensor':
            test_sensor_sender()
        elif mode == 'control-recv':
            test_control_receiver()
        elif mode == 'control-send':
            test_control_sender()
        elif mode == 'bidirectional':
            test_bidirectional()
        else:
            print(f"Unknown mode: {mode}")
            print_usage()
    else:
        # Run all tests
        print("Running all tests...\n")
        test_sensor_sender()
        time.sleep(1)
        test_control_sender()
        print("\n" + "="*60)
        print("  All tests completed!")
        print("="*60 + "\n")


def print_usage():
    """Print usage information"""
    print("Usage:")
    print("  python test_udp.py                  # Run all tests")
    print("  python test_udp.py sensor           # Test sensor data sending")
    print("  python test_udp.py control-recv     # Test control receiving")
    print("  python test_udp.py control-send     # Test control sending")
    print("  python test_udp.py bidirectional    # Test full loop")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

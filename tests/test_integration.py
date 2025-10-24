"""
Integration tests for CARLA-DORA system
"""

import unittest
import socket
import time
import msgpack
from carla_agent.agent_wrapper import DoraUDPBridge


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_udp_communication(self):
        """Test UDP communication between CARLA and DORA"""
        
        # Create sender (simulating CARLA agent)
        sender = DoraUDPBridge(
            carla_to_dora_port=10001,
            dora_to_carla_port=10002
        )
        
        # Create receiver socket (simulating DORA)
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver.bind(('localhost', 10001))
        receiver.settimeout(1.0)
        
        # Send test data
        test_data = {
            'gps': {'latitude': 1.0, 'longitude': 2.0},
            'speed': 20.0,
            'timestamp': time.time()
        }
        
        sender.send_sensor_data(test_data)
        
        # Receive and verify
        data, addr = receiver.recvfrom(4096)
        received = msgpack.unpackb(data, raw=False)
        
        self.assertEqual(received['speed'], 20.0)
        self.assertEqual(received['gps']['latitude'], 1.0)
        
        # Cleanup
        sender.close()
        receiver.close()
    
    def test_control_loop(self):
        """Test control command loop"""
        
        # Create bridge
        bridge = DoraUDPBridge(
            carla_to_dora_port=10003,
            dora_to_carla_port=10004
        )
        
        # Create control sender (simulating DORA)
        control_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Send control command
        control = {
            'throttle': 0.5,
            'steer': 0.0,
            'brake': 0.0
        }
        
        packed = msgpack.packb(control, use_bin_type=True)
        control_sender.sendto(packed, ('localhost', 10004))
        
        # Give it a moment to arrive
        time.sleep(0.1)
        
        # Receive control
        received_control = bridge.receive_control()
        
        # Verify
        if received_control:
            self.assertEqual(received_control['throttle'], 0.5)
            self.assertEqual(received_control['steer'], 0.0)
        
        # Cleanup
        bridge.close()
        control_sender.close()


if __name__ == '__main__':
    unittest.main()

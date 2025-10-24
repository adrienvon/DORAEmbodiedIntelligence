"""
Unit tests for CARLA Agent
"""

import unittest
from unittest.mock import Mock, patch
from carla_agent.agent_wrapper import CarlaDoraAgent, DoraUDPBridge


class TestDoraUDPBridge(unittest.TestCase):
    """Test cases for UDP bridge"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bridge = DoraUDPBridge(
            carla_to_dora_port=9001,
            dora_to_carla_port=9002
        )
    
    def tearDown(self):
        """Clean up after tests"""
        self.bridge.close()
    
    def test_send_sensor_data(self):
        """Test sending sensor data"""
        test_data = {
            'gps': {'latitude': 0.0, 'longitude': 0.0},
            'speed': 10.0
        }
        
        result = self.bridge.send_sensor_data(test_data)
        self.assertTrue(result)
    
    def test_receive_control_timeout(self):
        """Test receiving control with timeout"""
        control = self.bridge.receive_control()
        # Should return None on timeout
        self.assertIsNone(control)


class TestCarlaDoraAgent(unittest.TestCase):
    """Test cases for CARLA DORA Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = CarlaDoraAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNone(self.agent.bridge)
        self.assertEqual(self.agent.step_count, 0)
    
    def test_sensors_definition(self):
        """Test sensor suite definition"""
        sensors = self.agent.sensors()
        
        # Should have GPS, IMU, Speed, and Camera
        self.assertGreaterEqual(len(sensors), 4)
        
        # Check sensor types
        sensor_types = [s['type'] for s in sensors]
        self.assertIn('sensor.other.gnss', sensor_types)
        self.assertIn('sensor.other.imu', sensor_types)
        self.assertIn('sensor.speedometer', sensor_types)
        self.assertIn('sensor.camera.rgb', sensor_types)
    
    def test_extract_sensor_data(self):
        """Test sensor data extraction"""
        mock_input = {
            'GPS': (0, [1.234, 5.678, 100.0]),
            'Speed': (0, {'speed': 15.5})
        }
        
        extracted = self.agent._extract_sensor_data(mock_input)
        
        self.assertIn('gps', extracted)
        self.assertIn('speed', extracted)
        self.assertEqual(extracted['speed'], 15.5)


if __name__ == '__main__':
    unittest.main()

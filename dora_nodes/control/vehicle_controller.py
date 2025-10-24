"""
Control Node
Converts planning output into vehicle control commands (throttle, steer, brake)
"""

import socket
import msgpack
import pyarrow as pa
from dora import Node


class PIDController:
    """Simple PID controller"""
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.01):
        """
        Initialize PID controller
        
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.previous_error = 0.0
        self.integral = 0.0
    
    def compute(self, setpoint: float, measured_value: float, dt: float = 0.05) -> float:
        """
        Compute control output
        
        Args:
            setpoint: Desired value
            measured_value: Current value
            dt: Time step
            
        Returns:
            Control output
        """
        error = setpoint - measured_value
        
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0
        
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        
        self.previous_error = error
        
        return output
    
    def reset(self):
        """Reset controller state"""
        self.previous_error = 0.0
        self.integral = 0.0


class VehicleController:
    """Vehicle control system"""
    
    def __init__(self, carla_host: str = 'localhost', carla_port: int = 8002):
        """
        Initialize vehicle controller
        
        Args:
            carla_host: Host to send control commands to
            carla_port: Port to send control commands to
        """
        self.speed_controller = PIDController(kp=0.5, ki=0.1, kd=0.05)
        self.steering_controller = PIDController(kp=1.0, ki=0.0, kd=0.1)
        
        # UDP socket for sending control commands
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.carla_addr = (carla_host, carla_port)
        
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.target_steering = 0.0
        
        print(f"[VehicleController] Initialized, sending to {carla_host}:{carla_port}")
    
    def update_plan(self, plan):
        """Update target values from planner"""
        self.target_speed = plan.get('target_speed', 0.0)
        self.target_steering = plan.get('target_steering', 0.0)
    
    def update_speed(self, speed):
        """Update current speed"""
        self.current_speed = speed
    
    def compute_control(self) -> dict:
        """
        Compute vehicle control commands
        
        Returns:
            Dictionary with throttle, steer, brake
        """
        # Speed control
        speed_error = self.target_speed - self.current_speed
        throttle_brake = self.speed_controller.compute(self.target_speed, self.current_speed)
        
        # Separate throttle and brake
        if throttle_brake > 0:
            throttle = min(max(throttle_brake, 0.0), 1.0)
            brake = 0.0
        else:
            throttle = 0.0
            brake = min(max(-throttle_brake, 0.0), 1.0)
        
        # Steering control (for now, use target directly)
        steer = max(min(self.target_steering, 1.0), -1.0)
        
        control = {
            'throttle': float(throttle),
            'steer': float(steer),
            'brake': float(brake)
        }
        
        return control
    
    def send_control(self, control: dict):
        """
        Send control commands via UDP
        
        Args:
            control: Control command dictionary
        """
        try:
            packed_data = msgpack.packb(control, use_bin_type=True)
            self.socket.sendto(packed_data, self.carla_addr)
        except Exception as e:
            print(f"[VehicleController] Error sending control: {e}")
    
    def close(self):
        """Close resources"""
        self.socket.close()


def main():
    """Main entry point for DORA node"""
    
    # Initialize DORA node
    node = Node()
    
    # Initialize controller
    controller = VehicleController()
    
    print("[VehicleController] Node started")
    
    try:
        # Main event loop
        for event in node:
            if event["type"] == "INPUT":
                event_id = event["id"]
                
                # Update current speed
                if event_id == "speed":
                    speed = event["value"][0].as_py()
                    controller.update_speed(speed)
                
                # Receive plan and compute control
                elif event_id == "plan":
                    plan = event["value"][0].as_py()
                    controller.update_plan(plan)
                    
                    # Compute control commands
                    control = controller.compute_control()
                    
                    # Send control to CARLA
                    controller.send_control(control)
                    
                    # Also output to DORA (for logging/debugging)
                    node.send_output(
                        "control",
                        pa.array([control]),
                        event["metadata"]["timestamp"]
                    )
                    
                    print(f"[VehicleController] Control: throttle={control['throttle']:.2f}, "
                          f"steer={control['steer']:.2f}, brake={control['brake']:.2f}")
    
    finally:
        controller.close()
        print("[VehicleController] Node stopped")


if __name__ == "__main__":
    main()

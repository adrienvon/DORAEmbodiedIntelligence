#!/usr/bin/env python3
"""
最小化传感器数据接收测试
不依赖 DORA 编排系统，直接监听 UDP 端口验证 CARLA 数据发送
"""

import socket
import msgpack
import time
from datetime import datetime

def main():
    # 监听 CARLA Agent 发送的传感器数据
    HOST = 'localhost'
    PORT = 8001
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.settimeout(1.0)  # 1秒超时
    
    print("=" * 70)
    print("🎯 最小化 UDP 接收测试")
    print("=" * 70)
    print(f"✅ 监听地址: {HOST}:{PORT}")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("\n等待 CARLA Agent 发送传感器数据...\n")
    
    packet_count = 0
    last_print_time = time.time()
    
    try:
        while True:
            try:
                data, addr = sock.recvfrom(65535)
                packet_count += 1
                
                # 解包 MessagePack 数据
                try:
                    sensor_data = msgpack.unpackb(data, raw=False)
                    
                    # 每秒打印一次详细信息
                    current_time = time.time()
                    if current_time - last_print_time >= 1.0:
                        print(f"\n{'='*70}")
                        print(f"📦 数据包 #{packet_count} | 时间: {datetime.now().strftime('%H:%M:%S')}")
                        print(f"{'='*70}")
                        
                        # 打印传感器数据
                        if 'gps' in sensor_data:
                            gps = sensor_data['gps']
                            print(f"  🗺️  GPS: lat={gps.get('latitude', 'N/A'):.6f}, "
                                  f"lon={gps.get('longitude', 'N/A'):.6f}")
                        
                        if 'speed' in sensor_data:
                            speed = sensor_data['speed']
                            print(f"  🚗 速度: {speed:.2f} m/s ({speed * 3.6:.2f} km/h)")
                        
                        if 'imu' in sensor_data:
                            imu = sensor_data['imu']
                            accel = imu.get('accelerometer', {})
                            print(f"  📊 IMU 加速度: x={accel.get('x', 0):.3f}, "
                                  f"y={accel.get('y', 0):.3f}, z={accel.get('z', 0):.3f}")
                        
                        if 'camera' in sensor_data:
                            camera = sensor_data['camera']
                            print(f"  📷 相机: {camera.get('width', 0)}x{camera.get('height', 0)}")
                        
                        if 'timestamp' in sensor_data:
                            print(f"  ⏱️  时间戳: {sensor_data['timestamp']:.6f}")
                        
                        print(f"  📈 总接收数据包: {packet_count}")
                        print(f"{'='*70}")
                        
                        last_print_time = current_time
                    else:
                        # 简单的点状进度指示
                        print(".", end="", flush=True)
                    
                except Exception as e:
                    print(f"\n⚠️  解析数据包失败: {e}")
                    print(f"   原始数据长度: {len(data)} bytes")
            
            except socket.timeout:
                # 超时，继续等待
                if packet_count == 0:
                    print(".", end="", flush=True)
                continue
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("⏹️  测试终止")
        print("=" * 70)
        print(f"✅ 总接收数据包数: {packet_count}")
        print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
    
    finally:
        sock.close()
        print("\n🔌 UDP 端口已关闭")

if __name__ == "__main__":
    main()

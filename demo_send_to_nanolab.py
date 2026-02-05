#!/usr/bin/env python3
"""
Demonstration script showing how the "Send to NanoLab" functionality works.
This simulates what happens when the user clicks the button.
"""

import sys
import os
import time
import serial
import serial.tools.list_ports

# Add the current directory to the path so we can import the GUI
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simulate_send_to_nanolab():
    """Simulate the send_to_nanolab functionality"""
    print("=== Simulating 'Send to NanoLab' Button Click ===\n")
    
    # Step 1: Check connection type
    print("1. Checking connection type...")
    connection_type = "USB Port"  # Simulating USB connection selected
    print(f"   Connection type: {connection_type}")
    
    if connection_type != "USB Port":
        print("   ❌ Cannot send: USB connection not selected")
        return False
    
    print("   ✓ USB connection selected")
    
    # Step 2: Find Arduino port
    print("\n2. Finding Arduino port...")
    ports = serial.tools.list_ports.comports()
    arduino_port = None
    
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                ser.close()
                arduino_port = port.device
                print(f"   ✓ Found Arduino at: {arduino_port}")
                break
            except:
                pass
    
    if not arduino_port:
        print("   ❌ Arduino not found on USB ports")
        return False
    
    # Step 3: Simulate saved settings (these would come from the GUI)
    print("\n3. Loading saved settings from GUI...")
    saved_settings = {
        'led_status': True,
        'led_color': (255, 165, 0),  # Orange
        'water_pump_status': True,
        'water_pump_speed': 75,
        'water_pump_flow': 15,
        'fan_status': True,
        'fan_intensity': 60,
        'sensor_status': True,
        'sensor_reading_interval': 10,
        'sensor_temp_threshold': 22,
        'sensor_humidity_threshold': 55
    }
    
    print("   ✓ Settings loaded:")
    print(f"     - LED: {'ON' if saved_settings['led_status'] else 'OFF'} (Color: RGB{saved_settings['led_color']})")
    print(f"     - Water Pump: {'ON' if saved_settings['water_pump_status'] else 'OFF'} (Speed: {saved_settings['water_pump_speed']}%, Flow: {saved_settings['water_pump_flow']} L/min)")
    print(f"     - Fan: {'ON' if saved_settings['fan_status'] else 'OFF'} (Intensity: {saved_settings['fan_intensity']}%)")
    print(f"     - Sensor: {'ON' if saved_settings['sensor_status'] else 'OFF'} (Temp: {saved_settings['sensor_temp_threshold']}°C, Humidity: {saved_settings['sensor_humidity_threshold']}%)")
    
    # Step 4: Send commands (simulated)
    print("\n4. Sending commands to Arduino...")
    
    # LED command
    if saved_settings['led_status']:
        r, g, b = saved_settings['led_color']
        brightness = 70  # Default brightness
        duration = 300   # Default duration
        interval = 60    # Default interval
        led_command = f"LED,ON,{r},{g},{b},{brightness},{duration},{interval}\n"
        print(f"   → {led_command.strip()}")
    else:
        led_command = "LED,OFF\n"
        print(f"   → {led_command.strip()}")
    
    # Water pump command
    status = "ON" if saved_settings['water_pump_status'] else "OFF"
    pump_command = f"PUMP,{status},{saved_settings['water_pump_speed']},{saved_settings['water_pump_flow']},300,60\n"
    print(f"   → {pump_command.strip()}")
    
    # Fan command
    status = "ON" if saved_settings['fan_status'] else "OFF"
    fan_command = f"FAN,{status},{saved_settings['fan_intensity']},300,60\n"
    print(f"   → {fan_command.strip()}")
    
    # Sensor command
    status = "ON" if saved_settings['sensor_status'] else "OFF"
    sensor_command = f"SENSOR,{status},{saved_settings['sensor_reading_interval']},{saved_settings['sensor_temp_threshold']},{saved_settings['sensor_humidity_threshold']},ON,10,ON,5,300,60\n"
    print(f"   → {sensor_command.strip()}")
    
    # Step 5: Simulate actual serial communication
    print("\n5. Opening serial connection...")
    try:
        ser = serial.Serial(arduino_port, 9600, timeout=1)
        time.sleep(2)  # Allow Arduino to reset
        
        print("   ✓ Serial connection opened")
        print("   ✓ Sending commands...")
        
        # In real implementation, these would be sent:
        # ser.write(led_command.encode())
        # ser.write(pump_command.encode())
        # ser.write(fan_command.encode())
        # ser.write(sensor_command.encode())
        
        ser.close()
        print("   ✓ Serial connection closed")
        
    except Exception as e:
        print(f"   ❌ Error in serial communication: {e}")
        return False
    
    print("\n🎉 All settings sent to NanoLab successfully!")
    return True

def main():
    print("This demonstrates what happens when you click 'Send to NanoLab' in the GUI.\n")
    
    success = simulate_send_to_nanolab()
    
    if success:
        print("\n✅ Simulation completed successfully!")
        print("\nIn the actual GUI:")
        print("1. User sets settings in individual pages (LED, Water Pump, Fan, Sensor)")
        print("2. User clicks 'Send to NanoLab' button on the main page")
        print("3. The GUI automatically sends all saved settings to the Arduino")
        print("4. User sees 'All settings sent to NanoLab successfully' in the console")
    else:
        print("\n❌ Simulation failed")

if __name__ == "__main__":
    main()
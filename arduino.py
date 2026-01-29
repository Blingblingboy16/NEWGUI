import serial
import time

PORT = "/dev/ttyACM0"   # change if needed
BAUD = 9600

arduino = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # allow Arduino to reset

def send(cmd):
    print("→", cmd)
    arduino.write((cmd + "\n").encode())
    time.sleep(0.05)
    while arduino.in_waiting:
        print("←", arduino.readline().decode().strip())

send("COLOR,255,0,0")
time.sleep(1)
send("COLOR,0,255,0")
time.sleep(1)
send("COLOR,0,0,255")
time.sleep(1)
send("OFF")
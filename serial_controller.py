import serial
import time

class Arduino:
    def __init__(self, port="/dev/ttyACM0", baud=9600):
        self.ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)

    def send(self, cmd):
        self.ser.write((cmd + "\n").encode())

    def read(self):
        if self.ser.in_waiting:
            return self.ser.readline().decode().strip()
        return None

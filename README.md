o# NanoLab Control Panel

NanoLab Control Panel is a desktop GUI application built using **Python** and **PyQt6**.  
It provides a centralized interface for reviewing NanoLab data and adjusting hardware settings such as LEDs, fan, water pump, camera, and atmospheric sensors.

This application is designed to be simple, clean, and easy to navigate.  
It includes a **light/dark theme toggle**, **page navigation history**, and a **color picker** for LED customization.

---

## Features

| Feature | Description |
|--------|-------------|
| **Welcome Screen** | Quick access to reviewing data or entering settings. |
| **Settings Menu** | Configurable navigation to each device setting panel. |
| **LED Color Control** | Choose LED color using a live **color wheel picker**, or enter HEX manually. |
| **Navigation History** | `Back` and `Forward` buttons work similar to a web browser. |
| **Theme Toggle** | Switch between **light mode** and **dark mode** instantly. |

---

## Interface Pages

- **Data Results**
- **Water Pump Settings**
- **LED Settings** *(includes color preview + color picker UI)*
- **Fan Settings**
- **Camera Settings**
- **Atmospheric Sensor**

---

## Requirements

Make sure you have Python 3.10+ installed.

Install required Python packages:

```bash
pip install PyQt6 pyserial
```

## ESP32 LED Control Setup

This project includes Arduino code for controlling RGB LEDs on an ESP32 board via USB serial communication.

### Hardware Setup

1. Connect an RGB LED to ESP32 GPIO pins:
   - Red LED to GPIO 12
   - Green LED to GPIO 13
   - Blue LED to GPIO 14
   - Use appropriate resistors (220-470 ohm) for each LED anode.

2. Connect the ESP32 to your computer via USB.

### Software Setup

1. Install Arduino IDE or VS Code with Arduino extension.

2. Open `esp32_led_control.ino` in Arduino IDE.

3. Select your ESP32 board (e.g., ESP32 Dev Module) and correct COM port.

4. Upload the sketch to the ESP32.

5. The ESP32 will print "ESP32 LED Control Ready" in serial monitor.

### Running the GUI

1. Run the Python GUI:
   ```bash
   python new.gui.py
   ```

2. In the main page, select "USB Port" for connection method.

3. Go to LED Settings page.

4. Adjust brightness, color, and status.

5. Click "Apply Settings" - the GUI will automatically find the ESP32 and send commands to control the LEDs.

The ESP32 responds to commands like: `LED:1,70,255,0,0` (status, brightness, r, g, b)

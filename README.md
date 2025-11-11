# NanoLab Control Panel

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
pip install PyQt6

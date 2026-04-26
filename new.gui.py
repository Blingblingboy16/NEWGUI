import sys
import random
import csv
import os
import numpy as np
import serial
import serial.tools.list_ports
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QStackedWidget, QSpacerItem, QSizePolicy, QColorDialog,
    QLineEdit, QToolBar, QComboBox, QDateEdit, QSpinBox, QSlider, QCheckBox, QGroupBox, QScrollArea, QInputDialog, QTabWidget, QTimeEdit, QStatusBar
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer
from PyQt6.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# ----- COLORS -----
LIGHT_BG = "#f2f7f2"
DARK_BG = "#2c2f2c"
GREEN = "#a8d5a2"
GREEN_DARK = "#2f4f2d"
TEXT_LIGHT = "black"
TEXT_DARK = "white"

def style_button(button):
    button.setMinimumHeight(48)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    # No inline styles needed; handled by global stylesheet


class GraphCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def wheelEvent(self, event):
        # Do not accept wheel events to allow scrolling on the page
        event.ignore()

class BasePage(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")  # for styling
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        # no inline styles, handled by global stylesheet
        layout.addWidget(title_label)

        self.body = QVBoxLayout()
        self.body.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.body.setSpacing(20)
        layout.addLayout(self.body)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def get_main_window(self):
        # Navigate up to MainWindow by traversing parents until finding one with units_system
        current = self
        while current:
            if hasattr(current, 'units_system'):
                return current
            current = current.parent()
        return None


class MainPage(BasePage):
    def __init__(self, switch):
        super().__init__("Auxora NanoLab Control")

        # Main container layout
        main_container = QVBoxLayout()
        main_container.setSpacing(30)

        # Status bar at the top
        status_layout = QHBoxLayout()
        status_layout.setSpacing(20)

        # Connection status indicator (dot)
        self.connection_status = QLabel("●")
        # default to red (no board) until poll updates
        self.connection_status.setStyleSheet("font-size: 24px; color: #c0392b; font-weight: bold;")
        status_layout.addWidget(self.connection_status)

        # Status text (exposed so MainWindow can update it)
        self.connection_text = QLabel("Board not detected")
        self.connection_text.setStyleSheet("font-size: 16px; font-weight: 600; color: #2f4f2d;")
        status_layout.addWidget(self.connection_text)

        # Last update
        last_update = QLabel("Last update: Just now")
        last_update.setStyleSheet("font-size: 14px; color: #666666;")
        status_layout.addWidget(last_update)
        status_layout.addStretch()

        # Connection dropdown
        connection_layout = QHBoxLayout()
        connection_layout.setSpacing(10)
        connection_label = QLabel("Connection:")
        connection_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["USB Port", "Wireless"])
        self.connection_combo.setMinimumHeight(36)
        self.connection_combo.currentTextChanged.connect(self.update_connection_status)
        connection_layout.addWidget(connection_label)
        connection_layout.addWidget(self.connection_combo)
        status_layout.addLayout(connection_layout)

        # Rescan button to manually trigger port poll
        self.rescan_btn = QPushButton("Rescan")
        self.rescan_btn.setMinimumHeight(36)
        self.rescan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rescan_btn.clicked.connect(lambda: (self.get_main_window() and self.get_main_window().poll_serial_ports()))
        connection_layout.addWidget(self.rescan_btn)

        main_container.addLayout(status_layout)

        # Two-column layout for main content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)

        # Left Column - Review Data Section
        data_widget = QWidget()
        data_widget.setProperty("isCard", True)
        data_layout = QVBoxLayout(data_widget)
        data_layout.setSpacing(20)

        # Data section header
        data_header = QLabel("Review NanoLab Data")
        data_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2f4f2d; margin-bottom: 10px;")
        data_layout.addWidget(data_header)

        # Data content
        data_content = QLabel("Monitor your experiments and view collected data. Track plant growth, sensor readings, and system performance over time.")
        data_content.setStyleSheet("font-size: 14px; color: #555555; line-height: 1.4;")
        data_content.setWordWrap(True)
        data_layout.addWidget(data_content)

        # Data action buttons
        data_btn_layout = QHBoxLayout()
        data_btn_layout.setSpacing(15)
        
        view_data_btn = QPushButton("View Experiment Graphing")
        view_data_btn.clicked.connect(lambda: switch("graph"))
        view_data_btn.setStyleSheet("""
            QPushButton {
                background-color: #a8d5a2;
                color: #1a3d1a;
                border: 2px solid #6bb37a;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6bb37a;
                color: white;
                border-color: #4a8a55;
            }
        """)
        data_btn_layout.addWidget(view_data_btn)
        data_btn_layout.addStretch()

        data_layout.addLayout(data_btn_layout)
        data_layout.addStretch()

        content_layout.addWidget(data_widget, 1)

        # Right Column - Adjust Settings Section
        settings_widget = QWidget()
        settings_widget.setProperty("isCard", True)
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(20)

        # Settings section header
        settings_header = QLabel("Adjust NanoLab Settings")
        settings_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2f4f2d; margin-bottom: 10px;")
        settings_layout.addWidget(settings_header)

        # Units system toggle
        units_layout = QHBoxLayout()
        units_layout.setSpacing(15)
        units_label = QLabel("Units:")
        units_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.units_combo = QComboBox()
        self.units_combo.addItems(["Metric", "Imperial"])
        self.units_combo.setCurrentText("Metric")
        self.units_combo.setMinimumHeight(40)
        self.units_combo.currentTextChanged.connect(self.change_units)
        units_layout.addWidget(units_label)
        units_layout.addWidget(self.units_combo)
        units_layout.addStretch()
        settings_layout.addLayout(units_layout)

        # Grid of setting buttons
        grid = QGridLayout()
        grid.setSpacing(15)

        buttons = [
            ("Water Pump", "water"),
            ("LED Settings", "led"),
            ("Fan Settings", "fan"),
            ("DC Motor", "dc"),
            ("Sensor", "sensor"),
            ("Schedule", "schedule"),
        ]

        row, col = 0, 0
        for text, target in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #a8d5a2;
                    color: black;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #2f4f2d;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #2f4f2d;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda _, t=target: switch(t))
            grid.addWidget(btn, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1

        settings_layout.addLayout(grid)
        settings_layout.addStretch()

        content_layout.addWidget(settings_widget, 1)

        main_container.addLayout(content_layout)

        # Bottom section with Settings Overview and Send to NanoLab buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        bottom_layout.setContentsMargins(0, 20, 0, 0)

        # Settings Overview button
        overview_btn = QPushButton("Settings Overview")
        overview_btn.clicked.connect(lambda: switch("overview"))
        overview_btn.setStyleSheet("""
            QPushButton {
                background-color: #a8d5a2;
                color: #1a3d1a;
                border: 2px solid #6bb37a;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6bb37a;
                color: white;
                border-color: #4a8a55;
            }
        """)

        # Send to NanoLab button
        send_btn = QPushButton("Send to NanoLab")
        send_btn.clicked.connect(self.send_to_nanolab)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #a8d5a2;
                color: #1a3d1a;
                border: 2px solid #6bb37a;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6bb37a;
                color: white;
                border-color: #4a8a55;
            }
        """)

        bottom_layout.addWidget(overview_btn)
        bottom_layout.addWidget(send_btn)
        bottom_layout.addStretch()

        main_container.addLayout(bottom_layout)
        main_container.addStretch()

        self.body.addLayout(main_container)

    def update_connection_status(self, text):
        """Update the connection status indicator"""
        if text == "USB Port":
            self.connection_status.setStyleSheet("font-size: 24px; color: #27ae60; font-weight: bold;")
        else:
            self.connection_status.setStyleSheet("font-size: 24px; color: #f39c12; font-weight: bold;")

    def change_units(self, text):
        main_window = self.get_main_window()
        main_window.units_system = "metric" if text == "Metric" else "imperial"
        print(f"Units changed to {main_window.units_system}")
        # Update all pages that display units
        if hasattr(main_window.water_page, 'update_units'):
            main_window.water_page.update_units()
        if hasattr(main_window.sensor_page, 'update_units'):
            main_window.sensor_page.update_units()

    def send_to_nanolab(self):
        """Send all saved settings to the Arduino via serial communication"""
        main_window = self.get_main_window()
        if main_window is None:
            return

        # Only send if USB connection is selected
        if self.connection_combo.currentText() != "USB Port":
            print("Cannot send to NanoLab: USB connection not selected")
            return

        # Find Arduino port
        port = self.find_arduino_port()
        if not port:
            print("Arduino not found on USB ports")
            return

        try:
            # Open serial connection (match ESP32 baud rate)
            ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(2)  # Allow Arduino to reset

            # Send LED settings
            self.send_led_settings(ser, main_window)

            # Send water pump settings
            self.send_water_pump_settings(ser, main_window)

            # Send fan settings
            self.send_fan_settings(ser, main_window)

            # Send DC motor settings
            if hasattr(self, 'send_motor_settings'):
                self.send_motor_settings(ser, main_window)

            # Send sensor settings
            self.send_sensor_settings(ser, main_window)

            # Send schedule settings
            self.send_schedule_settings(ser, main_window)

            # Close serial connection
            ser.close()
            print("All settings sent to NanoLab successfully")

        except Exception as e:
            print(f"Error sending settings to Arduino: {e}")

    def find_arduino_port(self):
        """Find the Arduino port by looking for common patterns"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'ACM' in port.device or 'USB' in port.device:
                try:
                    # Try to open the port briefly to test if it's the Arduino
                    ser = serial.Serial(port.device, 115200, timeout=1)
                    ser.close()
                    return port.device
                except:
                    pass
        return None

    def send_led_settings(self, ser, main_window):
        """Send LED settings to Arduino using proper command format"""
        if not main_window.led_status:
            # Turn off LEDs
            command = "LED,OFF\n"
            ser.write(command.encode())
            print(f"Sent to Arduino: {command.strip()}")
            return

        # Parse color
        r, g, b = LEDSettingsPage.normalize_led_color(main_window.led_color)
        
        # Use saved brightness, duration, and interval values
        brightness = main_window.led_brightness
        duration = main_window.led_duration  # in seconds
        interval = main_window.led_interval  # in minutes
        
        # Send LED command in format: LED,ON,r,g,b,brightness,runSec,intervalMin
        command = f"LED,ON,{r},{g},{b},{brightness},{duration},{interval}\n"
        ser.write(command.encode())
        print(f"Sent to Arduino: {command.strip()}")

    def send_water_pump_settings(self, ser, main_window):
        """Send water pump settings to Arduino using proper command format"""
        if not main_window.water_pump_status:
            # Turn off pump
            command = "PUMP,OFF\n"
            ser.write(command.encode())
            print(f"Sent to Arduino: {command.strip()}")
            return

        # Use saved pump speed as percentage (0-100%)
        pump_speed = main_window.water_pump_speed
        duration = main_window.water_pump_duration  # in seconds
        interval = main_window.water_pump_interval  # in minutes
        
        # Send PUMP command in format: PUMP,SET,Speed%,DurationSec,IntervalMin
        command = f"PUMP,SET,{pump_speed},{duration},{interval}\n"
        ser.write(command.encode())
        print(f"Sent to Arduino: {command.strip()}")

    def send_fan_settings(self, ser, main_window):
        """Send fan settings to Arduino using proper command format"""
        if not main_window.fan_status:
            # Turn off fan
            command = "FAN,OFF\n"
            ser.write(command.encode())
            print(f"Sent to Arduino: {command.strip()}")
            return

        # Use saved fan intensity as speed (0-255 range)
        fan_speed = int((main_window.fan_intensity / 100) * 255)
        duration = main_window.fan_duration  # in seconds
        interval = main_window.fan_interval  # in minutes
        
        # Send FAN command in format: FAN,ON,speed,runSec,intervalMin
        command = f"FAN,ON,{fan_speed},{duration},{interval}\n"
        ser.write(command.encode())
        print(f"Sent to Arduino: {command.strip()}")

    def send_motor_settings(self, ser, main_window):
        """Send DC motor settings to Arduino using MOTOR_CFG command format"""
        # MOTOR_CFG,status(0/1),speed(0-255),onSec,offMin
        status = 1 if getattr(main_window, 'dc_enabled', False) else 0
        speed = getattr(main_window, 'dc_speed', 0)
        onSec = getattr(main_window, 'dc_on_duration', 0)
        offMin = getattr(main_window, 'dc_off_interval', 0)

        command = f"MOTOR_CFG,{status},{speed},{onSec},{offMin}\n"
        ser.write(command.encode())
        print(f"Sent to Arduino: {command.strip()}")

    def send_sensor_settings(self, ser, main_window):
        """Send sensor settings to Arduino"""
        status = "ON" if main_window.sensor_status else "OFF"
        reading_interval = main_window.sensor_reading_interval
        temp_threshold = main_window.sensor_temp_threshold
        humidity_threshold = main_window.sensor_humidity_threshold
        dht_status = "ON" if main_window.dht_status else "OFF"
        dht_threshold = main_window.dht_threshold
        voc_status = "ON" if main_window.voc_status else "OFF"
        voc_threshold = main_window.voc_threshold
        duration = main_window.sensor_duration
        interval = main_window.sensor_interval
        
        command = f"SENSOR,{status},{reading_interval},{temp_threshold},{humidity_threshold},{dht_status},{dht_threshold},{voc_status},{voc_threshold},{duration},{interval}\n"
        ser.write(command.encode())
        print(f"Sent to Arduino: {command.strip()}")

    def send_schedule_settings(self, ser, main_window):
        """Send schedule settings to Arduino"""
        if not hasattr(main_window, 'schedule_enabled') or not main_window.schedule_enabled:
            # Send schedule disable command
            command = "SCHEDULE,OFF\n"
            ser.write(command.encode())
            print(f"Sent to Arduino: {command.strip()}")
            return

        # Parse schedule settings
        start_date = main_window.schedule_start_date.toString("yyyy-MM-dd")
        end_date = main_window.schedule_end_date.toString("yyyy-MM-dd")
        start_time = main_window.schedule_start_time.toString("HH:mm")
        end_time = main_window.schedule_end_time.toString("HH:mm")
        
        # Send schedule command in format: SCHEDULE,ON,start_date,end_date,start_time,end_time
        command = f"SCHEDULE,ON,{start_date},{end_date},{start_time},{end_time}\n"
        ser.write(command.encode())
        print(f"Sent to Arduino: {command.strip()}")

    def get_main_window(self):
        # Navigate up to MainWindow by traversing parents until finding one with units_system
        current = self
        while current:
            if hasattr(current, 'units_system'):
                return current
            current = current.parent()
        return None

class WaterPumpPage(BasePage):
    def __init__(self, switch):
        super().__init__("Water Pump Settings")

        # Pump status toggle
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        status_label = QLabel("Pump Status:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.pump_toggle = QCheckBox("On/Off")
        self.pump_toggle.setChecked(True)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.pump_toggle)
        status_layout.addStretch()

        self.body.addLayout(status_layout)

        # Speed slider
        speed_layout = QVBoxLayout()
        speed_layout.setSpacing(10)
        speed_label = QLabel("Pump Speed: 50%")
        speed_label.setStyleSheet("font-size: 14px;")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(lambda v: speed_label.setText(f"Pump Speed: {v}%"))

        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        self.body.addLayout(speed_layout)

        # Flow rate spinbox
        flow_layout = QHBoxLayout()
        flow_layout.setSpacing(15)
        self.flow_label = QLabel("Flow Rate (L/min):")
        self.flow_label.setStyleSheet("font-size: 14px;")
        self.flow_spinbox = QSpinBox()
        self.flow_spinbox.setMinimum(0)
        self.flow_spinbox.setMaximum(20)
        self.flow_spinbox.setValue(10)
        flow_layout.addWidget(self.flow_label)
        flow_layout.addWidget(self.flow_spinbox)
        flow_layout.addStretch()

        self.body.addLayout(flow_layout)

        # Update units
        self.update_units()

        # Duration settings
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(15)
        duration_label = QLabel("Run Duration (seconds):")
        duration_label.setStyleSheet("font-size: 14px;")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(3600)
        self.duration_spinbox.setValue(300)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spinbox)
        duration_layout.addStretch()

        self.body.addLayout(duration_layout)

        # Interval settings
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(15)
        interval_label = QLabel("Run Interval (minutes):")
        interval_label.setStyleSheet("font-size: 14px;")
        self.run_interval_spinbox = QSpinBox()
        self.run_interval_spinbox.setMinimum(1)
        self.run_interval_spinbox.setMaximum(1440)
        self.run_interval_spinbox.setValue(60)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.run_interval_spinbox)
        interval_layout.addStretch()

        self.body.addLayout(interval_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_water_pump)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

    def update_units(self):
        main_window = self.get_main_window()
        if main_window is not None:
            if main_window.units_system == "metric":
                self.flow_label.setText("Flow Rate (L/min):")
            else:
                self.flow_label.setText("Flow Rate (GPM):")

    def apply_water_pump(self):
        main_window = self.get_main_window()
        if main_window is None:
            return
        main_window.water_pump_status = self.pump_toggle.isChecked()
        main_window.water_pump_speed = self.speed_slider.value()
        main_window.water_pump_flow = self.flow_spinbox.value()
        main_window.water_pump_duration = self.duration_spinbox.value()
        main_window.water_pump_interval = self.run_interval_spinbox.value()
        main_window.overview_page.update_labels()
        print("Water pump settings applied")
        # Friendly UX: notify user
        if main_window is not None and hasattr(main_window, 'show_temporary_message'):
            main_window.show_temporary_message("settings saved!", 2500)

class LEDSettingsPage(BasePage):
    def __init__(self, switch):
        super().__init__("LED Settings")

        # LED status toggle
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        status_label = QLabel("LED Status:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.led_toggle = QCheckBox("On/Off")
        self.led_toggle.setChecked(True)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.led_toggle)
        status_layout.addStretch()

        self.body.addLayout(status_layout)

        # Brightness slider
        brightness_layout = QVBoxLayout()
        brightness_layout.setSpacing(10)
        brightness_label = QLabel("Brightness: 70%")
        brightness_label.setStyleSheet("font-size: 14px;")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(70)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.brightness_slider.setTickInterval(10)
        self.brightness_slider.valueChanged.connect(lambda v: brightness_label.setText(f"Brightness: {v}%"))

        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        self.body.addLayout(brightness_layout)

        # Color preview
        color_preview_layout = QHBoxLayout()
        color_preview_layout.setSpacing(15)
        color_preview_label = QLabel("Color Preview:")
        color_preview_label.setStyleSheet("font-size: 14px;")
        self.color_display = QLabel()
        self.color_display.setFixedSize(60, 60)
        self.color_display.setStyleSheet("background-color: #ffffff; border: 2px solid black;")
        color_preview_layout.addWidget(color_preview_label)
        color_preview_layout.addWidget(self.color_display)
        color_preview_layout.addStretch()

        self.body.addLayout(color_preview_layout)

        # RGB Sliders
        rgb_sliders_layout = QVBoxLayout()
        rgb_sliders_layout.setSpacing(10)
        
        # Red slider
        red_layout = QHBoxLayout()
        red_layout.setSpacing(15)
        red_label = QLabel("Red:")
        red_label.setStyleSheet("font-size: 14px;")
        self.red_slider = QSlider(Qt.Orientation.Horizontal)
        self.red_slider.setMinimum(0)
        self.red_slider.setMaximum(255)
        self.red_slider.setValue(255)
        self.red_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.red_slider.setTickInterval(51)
        self.red_value_label = QLabel("255")
        self.red_value_label.setStyleSheet("font-size: 14px; min-width: 30px;")
        self.red_slider.valueChanged.connect(lambda v: self.update_rgb_display())
        red_layout.addWidget(red_label)
        red_layout.addWidget(self.red_slider)
        red_layout.addWidget(self.red_value_label)
        rgb_sliders_layout.addLayout(red_layout)

        # Green slider
        green_layout = QHBoxLayout()
        green_layout.setSpacing(15)
        green_label = QLabel("Green:")
        green_label.setStyleSheet("font-size: 14px;")
        self.green_slider = QSlider(Qt.Orientation.Horizontal)
        self.green_slider.setMinimum(0)
        self.green_slider.setMaximum(255)
        self.green_slider.setValue(255)
        self.green_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.green_slider.setTickInterval(51)
        self.green_value_label = QLabel("255")
        self.green_value_label.setStyleSheet("font-size: 14px; min-width: 30px;")
        self.green_slider.valueChanged.connect(lambda v: self.update_rgb_display())
        green_layout.addWidget(green_label)
        green_layout.addWidget(self.green_slider)
        green_layout.addWidget(self.green_value_label)
        rgb_sliders_layout.addLayout(green_layout)

        # Blue slider
        blue_layout = QHBoxLayout()
        blue_layout.setSpacing(15)
        blue_label = QLabel("Blue:")
        blue_label.setStyleSheet("font-size: 14px;")
        self.blue_slider = QSlider(Qt.Orientation.Horizontal)
        self.blue_slider.setMinimum(0)
        self.blue_slider.setMaximum(255)
        self.blue_slider.setValue(255)
        self.blue_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.blue_slider.setTickInterval(51)
        self.blue_value_label = QLabel("255")
        self.blue_value_label.setStyleSheet("font-size: 14px; min-width: 30px;")
        self.blue_slider.valueChanged.connect(lambda v: self.update_rgb_display())
        blue_layout.addWidget(blue_label)
        blue_layout.addWidget(self.blue_slider)
        blue_layout.addWidget(self.blue_value_label)
        rgb_sliders_layout.addLayout(blue_layout)

        self.body.addLayout(rgb_sliders_layout)

        # Color picker button
        color_picker_layout = QHBoxLayout()
        color_picker_layout.setSpacing(15)
        color_picker_label = QLabel("Or use color picker:")
        color_picker_label.setStyleSheet("font-size: 14px;")
        pick_btn = QPushButton("Pick Color")
        pick_btn.clicked.connect(self.pick_color)
        color_picker_layout.addWidget(color_picker_label)
        color_picker_layout.addWidget(pick_btn)
        color_picker_layout.addStretch()

        self.body.addLayout(color_picker_layout)

        # Duration settings
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(15)
        duration_label = QLabel("Run Duration (seconds):")
        duration_label.setStyleSheet("font-size: 14px;")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(3600)
        self.duration_spinbox.setValue(300)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spinbox)
        duration_layout.addStretch()

        self.body.addLayout(duration_layout)

        # Interval settings
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(15)
        interval_label = QLabel("Run Interval (minutes):")
        interval_label.setStyleSheet("font-size: 14px;")
        self.run_interval_spinbox = QSpinBox()
        self.run_interval_spinbox.setMinimum(1)
        self.run_interval_spinbox.setMaximum(1440)
        self.run_interval_spinbox.setValue(60)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.run_interval_spinbox)
        interval_layout.addStretch()

        self.body.addLayout(interval_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_led)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

    def update_rgb_display(self):
        """Update the color display and value labels based on slider values"""
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()
        
        # Update value labels
        self.red_value_label.setText(str(r))
        self.green_value_label.setText(str(g))
        self.blue_value_label.setText(str(b))
        
        # Update color display
        color = QColor(r, g, b)
        self.color_display.setStyleSheet(f"background-color: {color.name()}; border: 2px solid black;")

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_display.setStyleSheet(f"background-color: {color.name()}; border: 2px solid black;")
            # Update sliders to match selected color
            self.red_slider.setValue(color.red())
            self.green_slider.setValue(color.green())
            self.blue_slider.setValue(color.blue())
            self.update_rgb_display()

    @staticmethod
    def normalize_led_color(color_value):
        if isinstance(color_value, tuple) and len(color_value) == 3:
            return color_value
        if isinstance(color_value, str):
            parts = [p.strip() for p in color_value.split(",") if p.strip()]
            if len(parts) == 3:
                try:
                    values = [max(0, min(255, int(p))) for p in parts]
                    return values[0], values[1], values[2]
                except ValueError:
                    pass
        color = QColor(color_value)
        if not color.isValid():
            color = QColor("#ffffff")
        return color.red(), color.green(), color.blue()

    def apply_led(self):
        main_window = self.get_main_window()
        if main_window is None:
            return
        main_window.led_status = self.led_toggle.isChecked()
        main_window.led_brightness = self.brightness_slider.value()
        # Get color from sliders
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()
        main_window.led_color = (r, g, b)
        main_window.led_duration = self.duration_spinbox.value()
        main_window.led_interval = self.run_interval_spinbox.value()

        main_window.overview_page.update_labels()

        # Send to ESP32 if USB connection selected
        if main_window.connection_combo.currentText() == "USB Port":
            self.send_led_to_esp32(main_window)

        print("LED settings applied")
        # Always show a friendly confirmation regardless of send outcome
        try:
            if main_window is not None and hasattr(main_window, 'show_temporary_message'):
                main_window.show_temporary_message("settings saved!", 2500)
        except Exception:
            print("settings saved!")

    def send_led_to_esp32(self, main_window):
        # Find ESP32 port
        port = self.find_esp32_port()
        if port:
            try:
                # Parse color
                r, g, b = self.normalize_led_color(main_window.led_color)

                # Open serial
                ser = serial.Serial(port, 115200, timeout=1)

                # Send command
                status = 1 if main_window.led_status else 0
                brightness = main_window.led_brightness
                command = f"LED:{status},{brightness},{r},{g},{b}\n"
                ser.write(command.encode())

                # Close serial
                ser.close()
                print("LED command sent to ESP32")
            except Exception as e:
                print(f"Error sending to ESP32: {e}")
        else:
            print("ESP32 not found on USB ports")

    def find_esp32_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'USB' in port.device or 'ACM' in port.device:
                try:
                    ser = serial.Serial(port.device, 115200, timeout=1)
                    ser.write(b'PING\n')
                    response = ser.readline().decode().strip()
                    ser.close()
                    if response == 'PONG':
                        return port.device
                except:
                    pass
        return None

class FanSettingsPage(BasePage):
    def __init__(self, switch):
        super().__init__("Fan Settings")

        # Fan status toggle
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        status_label = QLabel("Fan Status:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.fan_toggle = QCheckBox("On/Off")
        self.fan_toggle.setChecked(True)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.fan_toggle)
        status_layout.addStretch()

        self.body.addLayout(status_layout)

        # Intensity slider
        intensity_layout = QVBoxLayout()
        intensity_layout.setSpacing(10)
        intensity_label = QLabel("Fan Intensity: 75%")
        intensity_label.setStyleSheet("font-size: 14px;")
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setMinimum(0)
        self.intensity_slider.setMaximum(100)
        self.intensity_slider.setValue(75)
        self.intensity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.intensity_slider.setTickInterval(10)
        self.intensity_slider.valueChanged.connect(lambda v: intensity_label.setText(f"Fan Intensity: {v}%"))

        intensity_layout.addWidget(intensity_label)
        intensity_layout.addWidget(self.intensity_slider)
        self.body.addLayout(intensity_layout)

        # Duration settings
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(15)
        duration_label = QLabel("Run Duration (seconds):")
        duration_label.setStyleSheet("font-size: 14px;")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(3600)
        self.duration_spinbox.setValue(300)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spinbox)
        duration_layout.addStretch()

        self.body.addLayout(duration_layout)

        # Interval settings
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(15)
        interval_label = QLabel("Run Interval (minutes):")
        interval_label.setStyleSheet("font-size: 14px;")
        self.run_interval_spinbox = QSpinBox()
        self.run_interval_spinbox.setMinimum(1)
        self.run_interval_spinbox.setMaximum(1440)
        self.run_interval_spinbox.setValue(60)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.run_interval_spinbox)
        interval_layout.addStretch()

        self.body.addLayout(interval_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_fan)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

    def apply_fan(self):
        main_window = self.get_main_window()
        if main_window is None:
            return
        main_window.fan_status = self.fan_toggle.isChecked()
        main_window.fan_intensity = self.intensity_slider.value()
        main_window.fan_duration = self.duration_spinbox.value()
        main_window.fan_interval = self.run_interval_spinbox.value()
        main_window.overview_page.update_labels()
        print("Fan settings applied")
        if main_window is not None and hasattr(main_window, 'show_temporary_message'):
            main_window.show_temporary_message("settings saved!", 2500)

class DCMotorPage(BasePage):
    def __init__(self, switch):
        super().__init__("DC Motor Settings")

        # DC Motor status toggle
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        status_label = QLabel("DC Motor Status:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.dc_toggle = QCheckBox("On/Off")
        self.dc_toggle.setChecked(True)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.dc_toggle)
        status_layout.addStretch()

        self.body.addLayout(status_layout)

        # Power percent slider
        power_layout = QVBoxLayout()
        power_layout.setSpacing(10)
        power_label = QLabel("Power: 70%")
        power_label.setStyleSheet("font-size: 14px;")
        self.power_slider = QSlider(Qt.Orientation.Horizontal)
        self.power_slider.setMinimum(0)
        self.power_slider.setMaximum(100)
        self.power_slider.setValue(70)
        self.power_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.power_slider.setTickInterval(10)
        self.power_slider.valueChanged.connect(lambda v: power_label.setText(f"Power: {v}%"))

        power_layout.addWidget(power_label)
        power_layout.addWidget(self.power_slider)
        self.body.addLayout(power_layout)

        # Duration settings (on seconds)
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(15)
        duration_label = QLabel("Run Duration (seconds):")
        duration_label.setStyleSheet("font-size: 14px;")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(3600)
        self.duration_spinbox.setValue(3600)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spinbox)
        duration_layout.addStretch()

        self.body.addLayout(duration_layout)

        # Interval settings (off minutes)
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(15)
        interval_label = QLabel("Off Interval (minutes):")
        interval_label.setStyleSheet("font-size: 14px;")
        self.run_interval_spinbox = QSpinBox()
        self.run_interval_spinbox.setMinimum(0)
        self.run_interval_spinbox.setMaximum(1440)
        self.run_interval_spinbox.setValue(0)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.run_interval_spinbox)
        interval_layout.addStretch()

        self.body.addLayout(interval_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_dc)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

    def apply_dc(self):
        main_window = self.get_main_window()
        if main_window is None:
            return
        main_window.dc_enabled = self.dc_toggle.isChecked()
        # Map 0-100% to 0-255 for Arduino command
        main_window.dc_speed = int((self.power_slider.value() / 100.0) * 255)
        main_window.dc_on_duration = self.duration_spinbox.value()
        main_window.dc_off_interval = self.run_interval_spinbox.value()
        main_window.overview_page.update_labels()
        print("DC motor settings applied")
        if main_window is not None and hasattr(main_window, 'show_temporary_message'):
            main_window.show_temporary_message("settings saved!", 2500)

class SensorPage(BasePage):
    def __init__(self, switch):
        super().__init__("Atmospheric Sensor Settings")

        # Sensor status toggle
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        status_label = QLabel("Sensor Status:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.sensor_toggle = QCheckBox("On/Off")
        self.sensor_toggle.setChecked(True)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.sensor_toggle)
        status_layout.addStretch()

        self.body.addLayout(status_layout)

        # Reading interval
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(15)
        interval_label = QLabel("Reading Interval (minutes):")
        interval_label.setStyleSheet("font-size: 14px;")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(60)
        self.interval_spinbox.setValue(5)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addStretch()

        self.body.addLayout(interval_layout)

<<<<<<< HEAD
    # Note: simplified sensor UI — only sensor On/Off and interval (minutes)
=======
    # (Other detailed sensor controls removed — page simplified)
>>>>>>> e2b7701 (updates)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_sensor)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

        # Update units
        self.update_units()

    def update_units(self):
        main_window = self.get_main_window()
        if main_window is not None:
            # No per-sensor unit labels in simplified UI
            pass

    def apply_sensor(self):
        main_window = self.get_main_window()
        if main_window is None:
            return
        # Only store the simplified sensor settings
        main_window.sensor_status = self.sensor_toggle.isChecked()
        # Only store simple settings: interval in minutes
        main_window.sensor_reading_interval = self.interval_spinbox.value()
        main_window.overview_page.update_labels()
        
        # Restart the live data timer with the new interval
        main_window.graph_page.restart_timer_with_new_interval()
        
        print("Sensor settings applied")
        if main_window is not None and hasattr(main_window, 'show_temporary_message'):
            main_window.show_temporary_message("settings saved!", 2500)

class SettingsOverviewPage(BasePage):
    def __init__(self, switch, main_window):
        super().__init__("Settings Overview")

        # Get main window reference
        self.main_window = main_window

        # Back to Main button at the top
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_btn = QPushButton("Back to Main")
        back_btn.clicked.connect(lambda: switch("main"))
        style_button(back_btn)
        back_layout.addWidget(back_btn)
        back_layout.addStretch()
        self.body.addLayout(back_layout)

        # Main layout for overview
        overview_layout = QVBoxLayout()
        overview_layout.setSpacing(15)

        # Water Pump Settings Overview
        water_group = QGroupBox("Water Pump")
        water_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        water_layout = QVBoxLayout()
        water_layout.setSpacing(10)
        water_layout.setContentsMargins(15, 15, 15, 15)

        self.water_labels = []
        water_settings_texts = [
            "Status: On",
            "Speed: 50%",
            "Flow Rate: 10 L/min",
            "Duration: 300 seconds",
            "Interval: 60 minutes"
        ]

        for text in water_settings_texts:
            setting_label = QLabel(text)
            setting_label.setStyleSheet("font-size: 14px;")
            water_layout.addWidget(setting_label)
            self.water_labels.append(setting_label)

        # Center the edit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_water_btn = QPushButton("Edit Water Pump Settings")
        edit_water_btn.clicked.connect(lambda: switch("water"))
        edit_water_btn.setStyleSheet("font-size: 14px; padding: 10px 20px; background-color: #6bb37a; color: white; border: none; border-radius: 6px;")
        btn_layout.addWidget(edit_water_btn)
        btn_layout.addStretch()
        water_layout.addLayout(btn_layout)

        water_group.setLayout(water_layout)
        overview_layout.addWidget(water_group)

        # DC Motor Settings Overview
        camera_group = QGroupBox("DC Motor")
        camera_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        camera_layout = QVBoxLayout()
        camera_layout.setSpacing(10)
        camera_layout.setContentsMargins(15, 15, 15, 15)

        self.camera_labels = []
        camera_settings_texts = [
            "Status: On",
            "Power: 70%",
            "Run Duration: 3600 seconds",
            "Off Interval: 0 minutes",
            "Raw Speed: 180"
        ]

        for text in camera_settings_texts:
            setting_label = QLabel(text)
            setting_label.setStyleSheet("font-size: 14px;")
            camera_layout.addWidget(setting_label)
            self.camera_labels.append(setting_label)

        # Center the edit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_camera_btn = QPushButton("Edit DC Motor Settings")
        edit_camera_btn.clicked.connect(lambda: switch("dc"))
        edit_camera_btn.setStyleSheet("font-size: 14px; padding: 10px 20px; background-color: #6bb37a; color: white; border: none; border-radius: 6px;")
        btn_layout.addWidget(edit_camera_btn)
        btn_layout.addStretch()
        camera_layout.addLayout(btn_layout)

        camera_group.setLayout(camera_layout)
        overview_layout.addWidget(camera_group)

        # Sensor Settings Overview
        sensor_group = QGroupBox("Atmospheric Sensor")
        sensor_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        sensor_layout = QVBoxLayout()
        sensor_layout.setSpacing(10)
        sensor_layout.setContentsMargins(15, 15, 15, 15)

        self.sensor_labels = []
        sensor_settings_texts = [
            "Status: On",
            "Reading Interval: 5 minutes",
<<<<<<< HEAD
            "DHT11 Status: On",
            "DHT11 Threshold: 10 cm",
            "VOC Status: On",
            "VOC Threshold: 5 ppm"
=======
>>>>>>> e2b7701 (updates)
        ]

        for text in sensor_settings_texts:
            setting_label = QLabel(text)
            setting_label.setStyleSheet("font-size: 14px;")
            sensor_layout.addWidget(setting_label)
            self.sensor_labels.append(setting_label)

        # Center the edit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_sensor_btn = QPushButton("Edit Sensor Settings")
        edit_sensor_btn.clicked.connect(lambda: switch("sensor"))
        edit_sensor_btn.setStyleSheet("font-size: 14px; padding: 10px 20px; background-color: #6bb37a; color: white; border: none; border-radius: 6px;")
        btn_layout.addWidget(edit_sensor_btn)
        btn_layout.addStretch()
        sensor_layout.addLayout(btn_layout)

        sensor_group.setLayout(sensor_layout)
        overview_layout.addWidget(sensor_group)

        # Schedule Settings Overview
        schedule_group = QGroupBox("Schedule")
        schedule_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        schedule_layout = QVBoxLayout()
        schedule_layout.setSpacing(10)
        schedule_layout.setContentsMargins(15, 15, 15, 15)

        self.schedule_labels = []
        schedule_settings_texts = [
            "Status: Disabled",
            "Start Date: Not set",
            "End Date: Not set",
            "Start Time: Not set",
            "End Time: Not set"
        ]

        for text in schedule_settings_texts:
            setting_label = QLabel(text)
            setting_label.setStyleSheet("font-size: 14px;")
            schedule_layout.addWidget(setting_label)
            self.schedule_labels.append(setting_label)

        # Center the edit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_schedule_btn = QPushButton("Edit Schedule Settings")
        edit_schedule_btn.clicked.connect(lambda: switch("schedule"))
        edit_schedule_btn.setStyleSheet("font-size: 14px; padding: 10px 20px; background-color: #6bb37a; color: white; border: none; border-radius: 6px;")
        btn_layout.addWidget(edit_schedule_btn)
        btn_layout.addStretch()
        schedule_layout.addLayout(btn_layout)

        schedule_group.setLayout(schedule_layout)
        overview_layout.addWidget(schedule_group)

        # Scroll area for the overview content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(overview_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(600)

        self.body.addWidget(scroll_area)

        # Reset settings button
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_btn = QPushButton("Reset Settings to Default")
        reset_btn.clicked.connect(self.reset_settings)
        reset_btn.setStyleSheet("font-size: 14px; padding: 10px 20px; background-color: #ff6b6b; color: white; border: none; border-radius: 6px;")
        reset_layout.addWidget(reset_btn)
        reset_layout.addStretch()
        self.body.addLayout(reset_layout)

        # Back button
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))
        self.body.addWidget(back_btn)

    def reset_settings(self):
        """Reset all settings to default values"""
        # Reset all settings to defaults
        self.main_window.water_pump_status = True
        self.main_window.water_pump_speed = 50
        self.main_window.water_pump_flow = 10
        self.main_window.water_pump_duration = 300
        self.main_window.water_pump_interval = 60

        self.main_window.led_status = True
        self.main_window.led_brightness = 70
        self.main_window.led_color = (255, 255, 255)
        self.main_window.led_duration = 300
        self.main_window.led_interval = 60

        self.main_window.fan_status = True
        self.main_window.fan_intensity = 75
        self.main_window.fan_duration = 300
        self.main_window.fan_interval = 60

        # DC Motor defaults
        self.main_window.dc_enabled = True
        self.main_window.dc_speed = 180  # 0-255
        self.main_window.dc_on_duration = 3600
        self.main_window.dc_off_interval = 0

        self.main_window.sensor_status = True
        self.main_window.sensor_reading_interval = 5
        self.main_window.sensor_temp_threshold = 25
        self.main_window.sensor_humidity_threshold = 60
        self.main_window.sensor_duration = 300
        self.main_window.sensor_interval = 60

        self.main_window.dht_status = True
        self.main_window.dht_threshold = 10
        self.main_window.voc_status = True
        self.main_window.voc_threshold = 5

        # Reset schedule
        self.main_window.schedule_enabled = False
        self.main_window.schedule_start_date = QDate.currentDate()
        self.main_window.schedule_end_date = QDate.currentDate().addDays(7)
        self.main_window.schedule_start_time = QTime(9, 0)
        self.main_window.schedule_end_time = QTime(17, 0)

        # Update all labels
        self.update_labels()
        print("Settings reset to default values")

    def update_labels(self):
        # Update water pump labels
        self.water_labels[0].setText(f"Status: {'On' if self.main_window.water_pump_status else 'Off'}")
        self.water_labels[1].setText(f"Speed: {self.main_window.water_pump_speed}%")
        self.water_labels[2].setText(f"Flow Rate: {self.main_window.water_pump_flow} L/min")
        self.water_labels[3].setText(f"Duration: {self.main_window.water_pump_duration} seconds")
        self.water_labels[4].setText(f"Interval: {self.main_window.water_pump_interval} minutes")

        # Update LED labels
        self.led_labels[0].setText(f"Status: {'On' if self.main_window.led_status else 'Off'}")
        self.led_labels[1].setText(f"Brightness: {self.main_window.led_brightness}%")
        r, g, b = LEDSettingsPage.normalize_led_color(self.main_window.led_color)
        self.led_labels[2].setText(f"Color: RGB({r}, {g}, {b})")
        self.led_labels[3].setText(f"Duration: {self.main_window.led_duration} seconds")
        self.led_labels[4].setText(f"Interval: {self.main_window.led_interval} minutes")

        # Update fan labels
        self.fan_labels[0].setText(f"Status: {'On' if self.main_window.fan_status else 'Off'}")
        self.fan_labels[1].setText(f"Intensity: {self.main_window.fan_intensity}%")
        self.fan_labels[2].setText(f"Duration: {self.main_window.fan_duration} seconds")
        self.fan_labels[3].setText(f"Interval: {self.main_window.fan_interval} minutes")

        # Update DC motor labels
        self.camera_labels[0].setText(f"Status: {'On' if self.main_window.dc_enabled else 'Off'}")
        # Show speed as percent
        speed_pct = int((self.main_window.dc_speed / 255.0) * 100)
        self.camera_labels[1].setText(f"Power: {speed_pct}%")
        self.camera_labels[2].setText(f"Run Duration: {self.main_window.dc_on_duration} seconds")
        self.camera_labels[3].setText(f"Off Interval: {self.main_window.dc_off_interval} minutes")
        # Ensure the fifth label (if present) is cleared or used for raw speed
        if len(self.camera_labels) > 4:
            self.camera_labels[4].setText(f"Raw Speed: {self.main_window.dc_speed}")

        # Update sensor labels
        self.sensor_labels[0].setText(f"Status: {'On' if self.main_window.sensor_status else 'Off'}")
        self.sensor_labels[1].setText(f"Reading Interval: {self.main_window.sensor_reading_interval} minutes")
        self.sensor_labels[2].setText(f"DHT11 Status: {'On' if self.main_window.dht_status else 'Off'}")
        self.sensor_labels[3].setText(f"DHT11 Threshold: {self.main_window.dht_threshold} cm")
        self.sensor_labels[4].setText(f"VOC Status: {'On' if self.main_window.voc_status else 'Off'}")
        self.sensor_labels[5].setText(f"VOC Threshold: {self.main_window.voc_threshold} ppm")

        # Update schedule labels
        if hasattr(self.main_window, 'schedule_enabled') and self.main_window.schedule_enabled:
            self.schedule_labels[0].setText("Status: Enabled")
            self.schedule_labels[1].setText(f"Start Date: {self.main_window.schedule_start_date.toString('MMM dd, yyyy')}")
            self.schedule_labels[2].setText(f"End Date: {self.main_window.schedule_end_date.toString('MMM dd, yyyy')}")
            self.schedule_labels[3].setText(f"Start Time: {self.main_window.schedule_start_time.toString('hh:mm AP')}")
            self.schedule_labels[4].setText(f"End Time: {self.main_window.schedule_end_time.toString('hh:mm AP')}")
        else:
            self.schedule_labels[0].setText("Status: Disabled")
            self.schedule_labels[1].setText("Start Date: Not set")
            self.schedule_labels[2].setText("End Date: Not set")
            self.schedule_labels[3].setText("Start Time: Not set")
            self.schedule_labels[4].setText("End Time: Not set")

class DataGraphPage(BasePage):
    def __init__(self, switch):
        super().__init__("NanoLab Data Visualization")

        # Create tab widget
        self.tabs = QTabWidget()
        self.body.addWidget(self.tabs)

        # Plant Growth Tab
        plant_tab = QWidget()
        plant_layout = QVBoxLayout(plant_tab)

        # Experiment selection
        experiment_layout = QHBoxLayout()
        experiment_layout.setSpacing(15)
        experiment_layout.addWidget(QLabel("Select Experiment:"))
        self.experiment_combo = QComboBox()
        self.experiment_combo.setMinimumHeight(40)
        experiment_layout.addWidget(self.experiment_combo)
        new_exp_btn = QPushButton("New Experiment")
        new_exp_btn.clicked.connect(self.create_new_experiment)
        experiment_layout.addWidget(new_exp_btn)
        experiment_layout.addStretch()
        plant_layout.addLayout(experiment_layout)

        # Create graph canvas
        self.plant_graph = GraphCanvas(self)

        # Interval display
        self.interval_label = QLabel("Last interval: N/A")
        self.interval_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        plant_layout.addWidget(self.interval_label)

        # Reset graph button
        reset_btn = QPushButton("Reset Graph")
        style_button(reset_btn)
        reset_btn.clicked.connect(self.reset_graph)
        plant_layout.addWidget(reset_btn)

        # Add plant graph
        plant_layout.addWidget(self.plant_graph)

        # Manual data entry
        manual_layout = QHBoxLayout()
        manual_layout.setSpacing(15)
        manual_layout.addWidget(QLabel("Time Since Start of Experiment (hours):"))
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Enter time in hours")
        manual_layout.addWidget(self.time_input)
        manual_layout.addWidget(QLabel("Length of your plant (cm):"))
        self.length_input = QLineEdit()
        self.length_input.setPlaceholderText("Enter plant length")
        manual_layout.addWidget(self.length_input)
        add_btn = QPushButton("Add Data Point")
        add_btn.clicked.connect(self.add_data_point)
        manual_layout.addWidget(add_btn)
        plant_layout.addLayout(manual_layout)

        self.tabs.addTab(plant_tab, "Plant Growth")

        # Sensor Data Tab
        sensor_tab = QWidget()
        sensor_layout = QVBoxLayout(sensor_tab)
        sensor_layout.setSpacing(20)

        # Create tab widget for different sensor graphs
        self.sensor_tabs = QTabWidget()
        
        # Temperature graph
        temp_widget = QWidget()
        temp_layout = QVBoxLayout(temp_widget)
        self.temp_graph = GraphCanvas(self)
        temp_layout.addWidget(self.temp_graph)
        self.sensor_tabs.addTab(temp_widget, "Temperature")

        # Humidity graph
        humidity_widget = QWidget()
        humidity_layout = QVBoxLayout(humidity_widget)
        self.humidity_graph = GraphCanvas(self)
        humidity_layout.addWidget(self.humidity_graph)
        self.sensor_tabs.addTab(humidity_widget, "Humidity")

        # Air Quality graph (VOC)
        air_quality_widget = QWidget()
        air_quality_layout = QVBoxLayout(air_quality_widget)
        self.air_quality_graph = GraphCanvas(self)
        air_quality_layout.addWidget(self.air_quality_graph)
        self.sensor_tabs.addTab(air_quality_widget, "Air Quality")

        sensor_layout.addWidget(self.sensor_tabs)

        # Right side: Sensor tracking info
        sensor_info_group = QGroupBox("Live Sensor Data")
        sensor_info_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        sensor_info_layout = QVBoxLayout()
        sensor_info_layout.setSpacing(10)
        sensor_info_layout.setContentsMargins(15, 15, 15, 15)

        # Sensor indicators with live data
        self.sensor_indicators = []
        sensor_names = [
            ("Temperature", "°C"),
            ("Humidity", "%"),
            ("Air Quality", "ppm")
        ]

        for name, unit in sensor_names:
            indicator_layout = QHBoxLayout()
            indicator_layout.setSpacing(10)
            status_label = QLabel("●")
            status_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
            name_label = QLabel(f"{name}:")
            name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            value_label = QLabel("N/A")
            value_label.setStyleSheet("font-size: 14px; color: #666666;")
            indicator_layout.addWidget(status_label)
            indicator_layout.addWidget(name_label)
            indicator_layout.addWidget(value_label)
            indicator_layout.addStretch()
            sensor_info_layout.addLayout(indicator_layout)
            self.sensor_indicators.append((status_label, name_label, value_label))

        sensor_info_layout.addStretch()
        sensor_info_group.setLayout(sensor_info_layout)
        sensor_layout.addWidget(sensor_info_group)

        # Tracking control buttons
        tracking_btn_layout = QHBoxLayout()
        tracking_btn_layout.setSpacing(15)
        
        self.start_tracking_btn = QPushButton("Start Sensor Tracking")
        self.start_tracking_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.start_tracking_btn.clicked.connect(self.start_sensor_tracking)
        
        self.stop_tracking_btn = QPushButton("Stop Sensor Tracking")
        self.stop_tracking_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.stop_tracking_btn.clicked.connect(self.stop_sensor_tracking)
        self.stop_tracking_btn.setEnabled(False)
        
        self.clear_tracking_btn = QPushButton("Clear Tracking Data")
        self.clear_tracking_btn.setStyleSheet("""
            QPushButton {
                background-color: #a8d5a2;
                color: #1a3d1a;
                border: 2px solid #6bb37a;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6bb37a;
                color: white;
                border-color: #4a8a55;
            }
        """)
        self.clear_tracking_btn.clicked.connect(self.clear_tracking_data)
        
        tracking_btn_layout.addWidget(self.start_tracking_btn)
        tracking_btn_layout.addWidget(self.stop_tracking_btn)
        tracking_btn_layout.addWidget(self.clear_tracking_btn)
        tracking_btn_layout.addStretch()
        
        sensor_layout.addLayout(tracking_btn_layout)

        # Serial debug log to display raw incoming serial lines (helps debugging)
        from PyQt6.QtWidgets import QTextEdit
        self.serial_log = QTextEdit()
        self.serial_log.setReadOnly(True)
        self.serial_log.setFixedHeight(140)
        self.serial_log.setPlaceholderText("Raw serial log (shows incoming MQ_DATA / DHT_DATA lines)...")
        sensor_layout.addWidget(self.serial_log)

        # Tracking status label
        self.tracking_status_label = QLabel("Tracking: Not Started")
        self.tracking_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #666666;")
        sensor_layout.addWidget(self.tracking_status_label)

        self.tabs.addTab(sensor_tab, "Sensor Data")

        # Bottom layout with back button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))
        bottom_layout.addWidget(back_btn)
        bottom_layout.addStretch()
        self.body.addLayout(bottom_layout)

        # Initialize live data timer
        self.live_data_timer = None
        
        # Sensor tracking data storage
        self.tracking_active = False
        self.tracking_start_time = None
        self.tracking_data = {
            'time': [],
            'temperature': [],
            'humidity': [],
            'voc': []
        }
        # Keep last-known sensor values so missing fields don't wipe previous readings
        self.last_temp = None
        self.last_humidity = None
        self.last_voc = None
        # Persistent serial connection (to avoid resetting Arduino on open/close)
        self.serial_conn = None
        
        self.start_live_data_updates()

    def start_live_data_updates(self):
        """Start the timer for live sensor data updates based on user interval setting"""
        main_window = self.get_main_window()
        if main_window is not None and main_window.sensor_status:
            interval_minutes = main_window.sensor_reading_interval
            interval_milliseconds = interval_minutes * 60 * 1000  # Convert to milliseconds
            if self.live_data_timer is not None:
                # Kill existing timer and restart with new interval
                self.killTimer(self.live_data_timer)
            # Try to open a persistent serial connection so we don't reset the
            # Arduino by opening/closing the port repeatedly. If opening fails
            # we still start the timer and use fallback values.
            try:
                if self.serial_conn is None:
                    port = None
                    if hasattr(main_window, 'find_arduino_port'):
                        port = main_window.find_arduino_port()
                    if port:
                        try:
                            self.serial_conn = serial.Serial(port, 115200, timeout=0.5)
                            try:
                                # Prevent toggling DTR which can reset some boards
                                self.serial_conn.setDTR(False)
                            except Exception:
                                pass
                        except Exception as e:
                            print(f"Could not open serial port {port}: {e}")
            except Exception:
                pass

            self.live_data_timer = self.startTimer(interval_milliseconds)
            # Initialize with immediate update
            self.update_live_sensor_data()

    def restart_timer_with_new_interval(self):
        """Restart the timer with a new interval from settings"""
        main_window = self.get_main_window()
        if main_window is not None and main_window.sensor_status:
            interval_minutes = main_window.sensor_reading_interval
            interval_milliseconds = max(1000, int(interval_minutes * 60 * 1000))  # Convert to milliseconds
            if self.live_data_timer is not None:
                self.killTimer(self.live_data_timer)
            self.live_data_timer = self.startTimer(interval_milliseconds)

    def start_sensor_tracking(self):
        """Start tracking sensor data with time stamps"""
        self.tracking_active = True
        self.tracking_start_time = time.time()
        # Clear previous tracking data
        self.tracking_data = {
            'time': [],
            'temperature': [],
            'humidity': [],
            'voc': []
        }
        
        # Ensure timer is started/restarted
        main_window = self.get_main_window()
        if main_window is not None:
            # When actively tracking, follow the user-configured sensor reading
            # interval so the GUI samples at the same cadence the user expects.
            interval_minutes = main_window.sensor_reading_interval
            sample_ms = max(1000, int(interval_minutes * 60 * 1000))
            if self.live_data_timer is not None:
                self.killTimer(self.live_data_timer)
            self.live_data_timer = self.startTimer(sample_ms)
            print(f"Tracking timer started with interval: {sample_ms} ms ({interval_minutes} min)")
        
        # Update UI
        self.start_tracking_btn.setEnabled(False)
        self.stop_tracking_btn.setEnabled(True)
        self.tracking_status_label.setText("Tracking: Active")
        self.tracking_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #27ae60;")
        
        # Get initial reading
        self.update_live_sensor_data()
        
        print("Sensor tracking started")

    def stop_sensor_tracking(self):
        """Stop tracking sensor data"""
        self.tracking_active = False
        
        # Update UI
        self.start_tracking_btn.setEnabled(True)
        self.stop_tracking_btn.setEnabled(False)
        self.tracking_status_label.setText(f"Tracking: Stopped ({len(self.tracking_data['time'])} data points)")
        self.tracking_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e74c3c;")
        
        # Update graphs with final data
        self.update_sensor_graphs()
        
        # Restore the normal live update interval from settings
        try:
            self.restart_timer_with_new_interval()
        except Exception:
            pass

        print(f"Sensor tracking stopped. Collected {len(self.tracking_data['time'])} data points")

    def clear_tracking_data(self):
        """Clear tracking data and reset graphs"""
        self.tracking_active = False
        self.tracking_start_time = None
        self.tracking_data = {
            'time': [],
            'temperature': [],
            'humidity': [],
            'voc': []
        }
        
        # Reset graphs
        self.temp_graph.ax.clear()
        self.temp_graph.ax.set_title("Temperature Over Time", fontsize=14, fontweight='bold')
        self.temp_graph.ax.set_xlabel("Time (minutes)", fontsize=12)
        self.temp_graph.ax.set_ylabel("Temperature (°C)", fontsize=12)
        self.temp_graph.ax.grid(True, alpha=0.3)
        self.temp_graph.draw()
        
        self.humidity_graph.ax.clear()
        self.humidity_graph.ax.set_title("Humidity Over Time", fontsize=14, fontweight='bold')
        self.humidity_graph.ax.set_xlabel("Time (minutes)", fontsize=12)
        self.humidity_graph.ax.set_ylabel("Humidity (%)", fontsize=12)
        self.humidity_graph.ax.grid(True, alpha=0.3)
        self.humidity_graph.draw()
        
        self.air_quality_graph.ax.clear()
        self.air_quality_graph.ax.set_title("Air Quality (VOC) Over Time", fontsize=14, fontweight='bold')
        self.air_quality_graph.ax.set_xlabel("Time (minutes)", fontsize=12)
        self.air_quality_graph.ax.set_ylabel("VOC (ppm)", fontsize=12)
        self.air_quality_graph.ax.grid(True, alpha=0.3)
        self.air_quality_graph.draw()
        
        # Update UI
        self.start_tracking_btn.setEnabled(True)
        self.stop_tracking_btn.setEnabled(False)
        self.tracking_status_label.setText("Tracking: Not Started")
        self.tracking_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #666666;")
        
        print("Tracking data cleared")

    def update_sensor_graphs(self):
        """Update all sensor graphs with tracked data"""
        if len(self.tracking_data['time']) == 0:
            return
        
        # Get temperature unit
        temp_unit = self.get_display_temperature_unit()
        
        # Convert temperature data if imperial
        display_temps = []
        for temp_c in self.tracking_data['temperature']:
            if temp_unit == "°F":
                display_temps.append((temp_c * 9/5) + 32)
            else:
                display_temps.append(temp_c)
            
        # Temperature graph
        self.temp_graph.ax.clear()
        self.temp_graph.ax.plot(self.tracking_data['time'], display_temps, 
                                'r-', linewidth=2, marker='o', markersize=4)
        self.temp_graph.ax.set_title("Temperature Over Time", fontsize=14, fontweight='bold')
        self.temp_graph.ax.set_xlabel("Time (minutes)", fontsize=12)
        self.temp_graph.ax.set_ylabel(f"Temperature ({temp_unit})", fontsize=12)
        self.temp_graph.ax.grid(True, alpha=0.3)
        self.temp_graph.draw()
        
        # Humidity graph
        self.humidity_graph.ax.clear()
        self.humidity_graph.ax.plot(self.tracking_data['time'], self.tracking_data['humidity'], 
                                     'b-', linewidth=2, marker='s', markersize=4)
        self.humidity_graph.ax.set_title("Humidity Over Time", fontsize=14, fontweight='bold')
        self.humidity_graph.ax.set_xlabel("Time (minutes)", fontsize=12)
        self.humidity_graph.ax.set_ylabel("Humidity (%)", fontsize=12)
        self.humidity_graph.ax.grid(True, alpha=0.3)
        self.humidity_graph.draw()
        
        # Air Quality graph
        self.air_quality_graph.ax.clear()
        self.air_quality_graph.ax.plot(self.tracking_data['time'], self.tracking_data['voc'], 
                                       'g-', linewidth=2, marker='^', markersize=4)
        self.air_quality_graph.ax.set_title("Air Quality (VOC) Over Time", fontsize=14, fontweight='bold')
        self.air_quality_graph.ax.set_xlabel("Time (minutes)", fontsize=12)
        self.air_quality_graph.ax.set_ylabel("VOC (ppm)", fontsize=12)
        self.air_quality_graph.ax.grid(True, alpha=0.3)
        self.air_quality_graph.draw()
        
        print("Sensor graphs updated")

    def timerEvent(self, event):
        """Handle timer events for live data updates"""
        self.update_live_sensor_data()

    def update_live_sensor_data(self):
        """Update the live sensor data display.

        This function now understands the ESP32/Arduino message formats emitted by
        the device: "MQ_DATA,raw,ppm" and "DHT_DATA,temp,humidity". It reads a
        small batch of lines from the serial buffer and updates the UI using
        the most recent values for each sensor. Missing fields keep their last
        known values to avoid flicker when only one sensor reports.
        """
        try:
            # Find Arduino port via the main window helper
            main_window = self.get_main_window()
            port = None
            if main_window is not None and hasattr(main_window, 'find_arduino_port'):
                port = main_window.find_arduino_port()

            # Temporary holders
            temp_value = None
            humidity_value = None
            voc_value = None

            # Use persistent serial connection if available; otherwise try to open one
            if self.serial_conn is None:
                if port:
                    try:
                        self.serial_conn = serial.Serial(port, 115200, timeout=0.5)
                        try:
                            self.serial_conn.setDTR(False)
                        except Exception:
                            pass
                    except Exception as e:
                        print(f"Could not open serial port {port}: {e}")

            if self.serial_conn:
                # Read up to a few lines from the buffer to pick up the latest values
                try:
                    for _ in range(10):
                        raw = self.serial_conn.readline()
                        if not raw:
                            break
                        try:
                            line = raw.decode().strip()
                        except Exception:
                            continue

                        if not line:
                            continue

                        # Append raw line to serial debug log (keep last 200 lines)
                        try:
                            if hasattr(self, 'serial_log') and self.serial_log is not None:
                                self.serial_log.append(line)
                                # Trim log: keep last ~200 lines
                                contents = self.serial_log.toPlainText().splitlines()
                                if len(contents) > 200:
                                    # keep last 200
                                    self.serial_log.setPlainText('\n'.join(contents[-200:]))
                        except Exception:
                            pass

                        # Parse MQ sensor line: MQ_DATA,rawADC,ppm
                        if line.startswith("MQ_DATA"):
                            parts = line.split(",")
                            if len(parts) >= 3:
                                try:
                                    ppm = float(parts[2])
                                    voc_value = ppm
                                except ValueError:
                                    pass

                        # Parse DHT sensor line: DHT_DATA,temp,humidity
                        elif line.startswith("DHT_DATA"):
                            parts = line.split(",")
                            if len(parts) >= 3:
                                try:
                                    temp_value = float(parts[1])
                                    humidity_value = float(parts[2])
                                except ValueError:
                                    pass
                except Exception as e:
                    print(f"Error reading from persistent serial connection: {e}")

            # Fill missing values with last known or fallback
            if temp_value is None:
                temp_value = self.last_temp
            if humidity_value is None:
                humidity_value = self.last_humidity
            if voc_value is None:
                voc_value = self.last_voc

            # If still missing, use fallback (random) values
            if temp_value is None or humidity_value is None or voc_value is None:
                ftemp, fhum, fvoc = self.get_fallback_values()
                if temp_value is None:
                    temp_value = ftemp
                if humidity_value is None:
                    humidity_value = fhum
                if voc_value is None:
                    voc_value = fvoc

            # Save last-known values
            self.last_temp = temp_value
            self.last_humidity = humidity_value
            self.last_voc = voc_value

            # Convert temperature for display
            display_temp, temp_unit = self.get_display_temperature(temp_value)

            # Update UI indicators
            self.sensor_indicators[0][2].setText(f"{display_temp}{temp_unit}")
            self.sensor_indicators[1][2].setText(f"{round(humidity_value, 2)}%")
            self.sensor_indicators[2][2].setText(f"{round(voc_value, 2)} ppm")

            # Ensure label text remains consistent
            self.sensor_indicators[0][1].setText("Temperature:")

            # Force repaint
            for indicator in self.sensor_indicators:
                indicator[2].repaint()

            # Store data if tracking is active (always store in Celsius for consistency)
            if self.tracking_active and self.tracking_start_time is not None:
                elapsed_minutes = (time.time() - self.tracking_start_time) / 60.0
                self.tracking_data['time'].append(elapsed_minutes)
                self.tracking_data['temperature'].append(temp_value)  # Store in Celsius
                self.tracking_data['humidity'].append(humidity_value)
                self.tracking_data['voc'].append(voc_value)
                # Update graphs in real-time
                self.update_sensor_graphs()

        except Exception as e:
            print(f"Error reading from Arduino: {e}")
            # On error, fall back to previous or random values and update UI
            temp_value = self.last_temp
            humidity_value = self.last_humidity
            voc_value = self.last_voc
            if temp_value is None or humidity_value is None or voc_value is None:
                temp_value, humidity_value, voc_value = self.get_fallback_values()

            display_temp, temp_unit = self.get_display_temperature(temp_value)
            self.sensor_indicators[0][2].setText(f"{display_temp}{temp_unit}")
            self.sensor_indicators[1][2].setText(f"{round(humidity_value,2)}%")
            self.sensor_indicators[2][2].setText(f"{round(voc_value,2)} ppm")
            for indicator in self.sensor_indicators:
                indicator[2].repaint()

    def get_fallback_values(self):
        """Generate random fallback values for testing"""
        # Temperature: 20-30°C (will be converted if imperial)
        temp_value = round(20 + (random.random() * 10), 1)
        
        # Humidity: 40-80%
        humidity_value = round(40 + (random.random() * 40), 1)
        
        # Air Quality: 0-100 ppm
        voc_value = round(random.random() * 100, 1)
        
        return temp_value, humidity_value, voc_value

    def get_display_temperature(self, celsius_value):
        """Convert temperature based on units system"""
        main_window = self.get_main_window()
        if main_window is not None and main_window.units_system == "imperial":
            # Convert Celsius to Fahrenheit
            fahrenheit = (celsius_value * 9/5) + 32
            return fahrenheit, "°F"
        return celsius_value, "°C"

    def get_display_temperature_unit(self):
        """Get the temperature unit based on units system"""
        main_window = self.get_main_window()
        if main_window is not None and main_window.units_system == "imperial":
            return "°F"
        return "°C"

    def close_serial_connection(self):
        """Close persistent serial connection if open."""
        try:
            if hasattr(self, 'serial_conn') and self.serial_conn:
                try:
                    self.serial_conn.close()
                except Exception:
                    pass
                self.serial_conn = None
        except Exception:
            pass

    def generate_fallback_data(self):
        """Generate random data when Arduino is not available"""
        temp_value, humidity_value, voc_value = self.get_fallback_values()
        
        self.sensor_indicators[0][2].setText(f"{temp_value}°C")
        self.sensor_indicators[1][2].setText(f"{humidity_value}%")
        self.sensor_indicators[2][2].setText(f"{voc_value} ppm")
        
        # Force immediate update of the display
        for indicator in self.sensor_indicators:
            indicator[2].repaint()

        # Initialize experiments
        self.load_experiments()

    def load_experiments(self):
        self.experiment_combo.clear()
        # Scan for experiment CSV files
        experiment_files = []
        for file in os.listdir('.'):
            if file.startswith('experiment_data_') and file.endswith('.csv') and file != 'experiment_data_manual.csv':
                experiment_files.append(file)
        experiment_files.sort()
        for file in experiment_files:
            # Extract name from filename
            name = file.replace('experiment_data_', '').replace('.csv', '').replace('_', ' ')
            self.experiment_combo.addItem(name, file)
        if self.experiment_combo.count() == 0:
            self.experiment_combo.addItem("No experiments", "")

    def create_new_experiment(self):
        name, ok = QInputDialog.getText(self, "New Experiment", "Enter experiment name:")
        if ok and name.strip():
            sanitized_name = name.strip().replace(' ', '_').replace('/', '_').replace('\\', '_')
            filename = f"experiment_data_{sanitized_name}.csv"
            if not os.path.exists(filename):
                with open(filename, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Time (hours)", "Plant Length (cm)"])
                self.load_experiments()
                # Select the new experiment
                for i in range(self.experiment_combo.count()):
                    if self.experiment_combo.itemData(i) == filename:
                        self.experiment_combo.setCurrentIndex(i)
                        break
            else:
                # Show message that name exists
                pass  # Could add QMessageBox

    def update_plant_graph(self):
        # Read experiment data from all CSV files
        experiment_data = []
        colors = ['b-', 'r-', 'c-', 'm-', 'y-', 'k-']
        markers = ['o', 's', '^', 'v', 'D', 'p']

        for i, file in enumerate(os.listdir('.')):
            if file.startswith('experiment_data_') and file.endswith('.csv') and file != 'experiment_data_manual.csv':
                try:
                    with open(file, "r") as f:
                        reader = csv.reader(f)
                        next(reader)  # Skip header
                        data = [(float(row[0]), float(row[1])) for row in reader if row]
                        if data:
                            name = file.replace('experiment_data_', '').replace('.csv', '').replace('_', ' ')
                            color = colors[i % len(colors)]
                            marker = markers[i % len(markers)]
                            experiment_data.append((name, data, color, marker))
                except Exception as e:
                    print(f"Error reading {file}: {e}")

        # Plot the data
        self.plant_graph.ax.clear()

        has_data = False
        for name, data, color, marker in experiment_data:
            if data:
                times, lengths = zip(*data)
                self.plant_graph.ax.plot(times, lengths, color, linewidth=2, markersize=6, marker=marker, label=name)
                has_data = True

        if has_data:
            self.plant_graph.ax.set_title("NanoLab Plant Growth Experiments", fontsize=16, fontweight='bold')
            self.plant_graph.ax.set_xlabel("Time Since Start of Experiment (hours)", fontsize=14)
            self.plant_graph.ax.set_ylabel("Plant Length (cm)", fontsize=14)
            self.plant_graph.ax.grid(True, alpha=0.3)
            self.plant_graph.ax.legend()
        else:
            # Fallback if no data found
            self.plant_graph.ax.text(0.5, 0.5, "No experiment data found.\nCreate a new experiment and add data points.",
                              horizontalalignment='center', verticalalignment='center', transform=self.plant_graph.ax.transAxes)

        self.plant_graph.draw()   # refresh canvas

    def update_sensor_graph(self):
        # For now, generate sample temperature data over time
        times = np.linspace(0, 24, 100)  # 24 hours
        temperatures = 20 + 5 * np.sin(2 * np.pi * times / 24) + np.random.normal(0, 1, 100)  # Sample temp variation

        self.sensor_graph.ax.clear()
        self.sensor_graph.ax.plot(times, temperatures, 'r-', linewidth=2, label="Temperature")
        self.sensor_graph.ax.set_title("Sensor Data: Temperature Over Time", fontsize=16, fontweight='bold')
        self.sensor_graph.ax.set_xlabel("Time Since Start of Experiment (hours)", fontsize=14)
        self.sensor_graph.ax.set_ylabel("Temperature (°C)", fontsize=14)
        self.sensor_graph.ax.grid(True, alpha=0.3)
        self.sensor_graph.ax.legend()
        self.sensor_graph.draw()

    def add_data_point(self):
        if self.experiment_combo.currentData() == "":
            return  # No valid experiment selected

        try:
            time_val = float(self.time_input.text())
            length = float(self.length_input.text())
            if length < 0 or time_val < 0:
                return
        except ValueError:
            return

        filename = self.experiment_combo.currentData()
        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time_val, length])

        self.time_input.clear()
        self.length_input.clear()
        self.update_plant_graph()

    def reset_graph(self):
        # Clear all experiment data files
        for file in os.listdir('.'):
            if file.startswith('experiment_data_') and file.endswith('.csv'):
                try:
                    os.remove(file)
                    print(f"Deleted experiment data file: {file}")
                except Exception as e:
                    print(f"Error deleting {file}: {e}")

        # Reload experiments to update the combo box
        self.load_experiments()

        # Clear the graph
        self.plant_graph.ax.clear()
        self.plant_graph.ax.text(0.5, 0.5, "Graph reset.\nAll experiment data cleared.\nYou can now start a new experiment.",
                          horizontalalignment='center', verticalalignment='center', transform=self.plant_graph.ax.transAxes)
        self.plant_graph.draw()
        print("Graph reset")

    def apply_settings(self):
        # Save manual data settings or confirm
        print("Graph settings applied - manual data saved")

class SchedulePage(BasePage):
    def __init__(self, switch):
        super().__init__("Schedule Settings")

        # Schedule status
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        status_label = QLabel("Schedule Status:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.schedule_toggle = QCheckBox("Enable Schedule")
        self.schedule_toggle.setChecked(False)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.schedule_toggle)
        status_layout.addStretch()

        self.body.addLayout(status_layout)

        # Date range selection
        date_layout = QVBoxLayout()
        date_layout.setSpacing(10)

        # Start date
        start_date_layout = QHBoxLayout()
        start_date_layout.setSpacing(15)
        start_date_label = QLabel("Start Date:")
        start_date_label.setStyleSheet("font-size: 14px;")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setMinimumDate(QDate.currentDate())
        start_date_layout.addWidget(start_date_label)
        start_date_layout.addWidget(self.start_date_edit)
        date_layout.addLayout(start_date_layout)

        # End date
        end_date_layout = QHBoxLayout()
        end_date_layout.setSpacing(15)
        end_date_label = QLabel("End Date:")
        end_date_label.setStyleSheet("font-size: 14px;")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(7))
        self.end_date_edit.setMinimumDate(QDate.currentDate())
        end_date_layout.addWidget(end_date_label)
        end_date_layout.addWidget(self.end_date_edit)
        date_layout.addLayout(end_date_layout)

        self.body.addLayout(date_layout)

        # Time range selection
        time_layout = QVBoxLayout()
        time_layout.setSpacing(10)

        # Start time
        start_time_layout = QHBoxLayout()
        start_time_layout.setSpacing(15)
        start_time_label = QLabel("Start Time:")
        start_time_label.setStyleSheet("font-size: 14px;")
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(9, 0))  # 9:00 AM
        start_time_layout.addWidget(start_time_label)
        start_time_layout.addWidget(self.start_time_edit)
        time_layout.addLayout(start_time_layout)

        # End time
        end_time_layout = QHBoxLayout()
        end_time_layout.setSpacing(15)
        end_time_label = QLabel("End Time:")
        end_time_label.setStyleSheet("font-size: 14px;")
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(17, 0))  # 5:00 PM
        end_time_layout.addWidget(end_time_label)
        end_time_layout.addWidget(self.end_time_edit)
        time_layout.addLayout(end_time_layout)

        self.body.addLayout(time_layout)

        # Schedule preview
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(15)
        preview_label = QLabel("Schedule Preview:")
        preview_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.schedule_preview = QLabel("No schedule set")
        self.schedule_preview.setStyleSheet("font-size: 14px; color: #666666;")
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.schedule_preview)
        preview_layout.addStretch()

        self.body.addLayout(preview_layout)

        # Schedule actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        # Update preview button
        update_preview_btn = QPushButton("Update Preview")
        update_preview_btn.clicked.connect(self.update_schedule_preview)
        
        # Clear schedule button
        clear_schedule_btn = QPushButton("Clear Schedule")
        clear_schedule_btn.clicked.connect(self.clear_schedule)
        
        actions_layout.addWidget(update_preview_btn)
        actions_layout.addWidget(clear_schedule_btn)
        actions_layout.addStretch()

        self.body.addLayout(actions_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        apply_btn = QPushButton("Apply Schedule")
        apply_btn.clicked.connect(self.apply_schedule)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

        # Initialize preview
        self.update_schedule_preview()

    def update_schedule_preview(self):
        """Update the schedule preview text"""
        if self.schedule_toggle.isChecked():
            start_date = self.start_date_edit.date().toString("MMM dd, yyyy")
            end_date = self.end_date_edit.date().toString("MMM dd, yyyy")
            start_time = self.start_time_edit.time().toString("hh:mm AP")
            end_time = self.end_time_edit.time().toString("hh:mm AP")
            
            preview_text = f"Active from {start_date} {start_time} to {end_date} {end_time}"
            self.schedule_preview.setText(preview_text)
            self.schedule_preview.setStyleSheet("font-size: 14px; color: #2f4f2d; font-weight: bold;")
        else:
            self.schedule_preview.setText("Schedule disabled")
            self.schedule_preview.setStyleSheet("font-size: 14px; color: #666666;")

    def clear_schedule(self):
        """Clear the schedule settings"""
        self.schedule_toggle.setChecked(False)
        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDate(QDate.currentDate().addDays(7))
        self.start_time_edit.setTime(QTime(9, 0))
        self.end_time_edit.setTime(QTime(17, 0))
        self.update_schedule_preview()
        print("Schedule cleared")

    def apply_schedule(self):
        """Apply the schedule settings"""
        main_window = self.get_main_window()
        if main_window is None:
            return
        
        # Store schedule settings
        main_window.schedule_enabled = self.schedule_toggle.isChecked()
        main_window.schedule_start_date = self.start_date_edit.date()
        main_window.schedule_end_date = self.end_date_edit.date()
        main_window.schedule_start_time = self.start_time_edit.time()
        main_window.schedule_end_time = self.end_time_edit.time()
        
        main_window.overview_page.update_labels()
        print("Schedule settings applied")
        if main_window is not None and hasattr(main_window, 'show_temporary_message'):
            main_window.show_temporary_message("settings saved!", 2500)

    def get_main_window(self):
        # Navigate up to MainWindow by traversing parents until finding one with units_system
        current = self
        while current:
            if hasattr(current, 'units_system'):
                return current
            current = current.parent()
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auxora NanoLab Control")
        self.setGeometry(100, 100, 1200, 800)

        # Navigation history
        self.page_history = []
        self.current_history_index = -1

        # Unit system
        self.units_system = "metric"  # "metric" or "imperial"

        # Settings storage
        self.water_pump_status = True
        self.water_pump_speed = 50
        self.water_pump_flow = 10
        self.water_pump_duration = 300
        self.water_pump_interval = 60

        self.led_status = True
        self.led_brightness = 70
        self.led_color = (255, 255, 255)
        self.led_duration = 300
        self.led_interval = 60

        self.fan_status = True
        self.fan_intensity = 75
        self.fan_duration = 300
        self.fan_interval = 60

        # DC motor defaults
        self.dc_enabled = True
        self.dc_speed = 180
        self.dc_on_duration = 3600
        self.dc_off_interval = 0

        self.sensor_status = True
        self.sensor_reading_interval = 5
        self.sensor_temp_threshold = 25
        self.sensor_humidity_threshold = 60
        self.sensor_duration = 300
        self.sensor_interval = 60

        self.dht_status = True
        self.dht_threshold = 10
        self.voc_status = True
        self.voc_threshold = 5

        self.stack = QStackedWidget()
        self.main_page = MainPage(self.switch_page)
        self.stack.addWidget(self.main_page)
        self.water_page = WaterPumpPage(self.switch_page)
        self.stack.addWidget(self.water_page)
        self.led_page = LEDSettingsPage(self.switch_page)
        self.stack.addWidget(self.led_page)
        self.fan_page = FanSettingsPage(self.switch_page)
        self.stack.addWidget(self.fan_page)
        self.dc_page = DCMotorPage(self.switch_page)
        self.stack.addWidget(self.dc_page)
        self.sensor_page = SensorPage(self.switch_page)
        self.stack.addWidget(self.sensor_page)
        self.graph_page = DataGraphPage(self.switch_page)
        self.stack.addWidget(self.graph_page)
        self.schedule_page = SchedulePage(self.switch_page)
        self.stack.addWidget(self.schedule_page)
        self.overview_page = SettingsOverviewPage(self.switch_page, self)
        self.stack.addWidget(self.overview_page)


        # Wrap the stacked widget in a scroll area for scrolling capability
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.stack)
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)

        # Global stylesheet — cleaner, modern look
        self.setStyleSheet(f"""
            /* Base */
            QMainWindow {{ background-color: {LIGHT_BG}; font-family: 'Segoe UI', Roboto, Arial, sans-serif; }}
            QWidget {{ color: {TEXT_LIGHT}; }}
            QLabel {{ font-size: 15px; color: #222222; }}
            #titleLabel {{ font-size: 26px; font-weight: 700; color: {GREEN_DARK}; margin-bottom: 8px; }}

            /* Buttons */
            QPushButton {{
                background-color: {GREEN};
                color: #ffffff;
                border: 0;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #7fcf87; }}
            QPushButton:pressed {{ background-color: #6bb37a; }}

            /* Inputs */
            QComboBox, QSpinBox, QLineEdit, QDateEdit, QTimeEdit {{
                background-color: #ffffff;
                border: 1px solid #d6d6d6;
                border-radius: 6px;
                padding: 6px;
            }}

            /* Cards */
            QWidget[isCard="true"] {{
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
            }}

            /* Groups */
            QGroupBox {{ font-weight: 700; border: 1px solid #e0e0e0; border-radius: 8px; margin-top: 8px; padding-top: 12px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; }}
        """)

        # Start a timer to poll serial ports and update board status
        self._port_poll_timer = QTimer(self)
        self._port_poll_timer.setInterval(2000)  # 2 seconds
        self._port_poll_timer.timeout.connect(self.poll_serial_ports)
        self._port_poll_timer.start()

        # Run an initial poll
        self.poll_serial_ports()

        # Ensure a visible status bar for user messages
        self._status = QStatusBar(self)
        self.setStatusBar(self._status)

        # Persistent in-UI flash label for reliable visibility on Linux
        self._flash_label = QLabel("", self)
        self._flash_label.setObjectName('flashLabel')
        self._flash_label.setStyleSheet(f"""
            QLabel#flashLabel {{
                background-color: {GREEN_DARK};
                color: white;
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: 700;
            }}
        """)
        self._flash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flash_label.hide()

    def switch_page(self, page_name):
        # Map page names to indices
        page_map = {
            "main": 0,
            "water": 1,
            "led": 2,
            "fan": 3,
            "dc": 4,
            "sensor": 5,
            "graph": 6,
            "schedule": 7,
            "overview": 8
        }
        if page_name in page_map:
            index = page_map[page_name]
            # Add to history
            if self.current_history_index == -1 or self.page_history[self.current_history_index] != index:
                # Remove future history if going to new page
                self.page_history = self.page_history[:self.current_history_index + 1]
                self.page_history.append(index)
                self.current_history_index += 1
            self.stack.setCurrentIndex(index)
            self.update_navigation_buttons()
        if page_name == "overview":
            self.overview_page.update_labels()

    def poll_serial_ports(self):
        """Check attached serial ports and update the main page's connection indicator.

        Strategy: look for ports whose device path contains common patterns like 'ACM' or 'USB'.
        If a USB port is present, mark board as detected. This keeps the check non-blocking.
        """
        try:
            ports = serial.tools.list_ports.comports()
            found = None
            for p in ports:
                dev = p.device or ''
                if 'ACM' in dev or 'USB' in dev or 'ttyUSB' in dev:
                    found = dev
                    break

            if found:
                # Update UI to show board detected (green)
                if hasattr(self, 'main_page'):
                    self.main_page.connection_status.setStyleSheet("font-size: 24px; color: #27ae60; font-weight: bold;")
                    self.main_page.connection_text.setText(f"Board: {found}")
            else:
                if hasattr(self, 'main_page'):
                    self.main_page.connection_status.setStyleSheet("font-size: 24px; color: #c0392b; font-weight: bold;")
                    self.main_page.connection_text.setText("Board not detected")
        except Exception:
            # On error, don't raise — just mark not detected
            if hasattr(self, 'main_page'):
                self.main_page.connection_status.setStyleSheet("font-size: 24px; color: #c0392b; font-weight: bold;")
                self.main_page.connection_text.setText("Board not detected")

    def go_back(self):
        if self.current_history_index > 0:
            self.current_history_index -= 1
            self.stack.setCurrentIndex(self.page_history[self.current_history_index])
            self.update_navigation_buttons()
            if self.stack.currentWidget() == self.overview_page:
                self.overview_page.update_labels()

    def go_forward(self):
        if self.current_history_index < len(self.page_history) - 1:
            self.current_history_index += 1
            self.stack.setCurrentIndex(self.page_history[self.current_history_index])
            self.update_navigation_buttons()
            if self.stack.currentWidget() == self.overview_page:
                self.overview_page.update_labels()

    def show_temporary_message(self, msg: str, ms: int = 3000):
        """Show a brief message in the window's status bar."""
        # Always attempt to show in the status bar
        try:
            if hasattr(self, '_status') and self._status is not None:
                self._status.showMessage(msg, ms)
        except Exception:
            # fallback to printing
            print(msg)

        # Additionally, create a floating, non-modal label overlay so the message
        # is visible regardless of status bar visibility or stylesheet.
        # Also show a persistent in-UI flash label so it is visible on all platforms (esp. Ubuntu)
        try:
            if hasattr(self, '_flash_label') and self._flash_label is not None:
                self._flash_label.setText(msg)
                self._flash_label.adjustSize()
                # Position bottom-center within the main window
                x = int((self.width() - self._flash_label.width()) / 2)
                y = self.height() - self._flash_label.height() - 100
                self._flash_label.move(max(10, x), max(10, y))
                self._flash_label.show()
                self._flash_label.raise_()

                # Auto-hide after ms
                QTimer.singleShot(ms, lambda: self._flash_label.hide())
        except Exception:
            pass

    def save_changes(self):
        current_index = self.stack.currentIndex()
        current_widget = self.stack.widget(current_index)
        # Try to call apply method if exists
        if hasattr(current_widget, 'apply_water_pump'):
            current_widget.apply_water_pump()
        elif hasattr(current_widget, 'apply_led'):
            current_widget.apply_led()
        elif hasattr(current_widget, 'apply_fan'):
            current_widget.apply_fan()
        elif hasattr(current_widget, 'apply_camera'):
            current_widget.apply_camera()
        elif hasattr(current_widget, 'apply_sensor'):
            current_widget.apply_sensor()
        elif hasattr(current_widget, 'apply_settings'):
            current_widget.apply_settings()
        else:
            print("No apply method for current page")
        self.overview_page.update_labels()

    def update_navigation_buttons(self):
        # Check if navigation buttons exist before trying to access them
        if hasattr(self, 'back_btn'):
            self.back_btn.setEnabled(self.current_history_index > 0)
        if hasattr(self, 'forward_btn'):
            self.forward_btn.setEnabled(self.current_history_index < len(self.page_history) - 1)

    def wheelEvent(self, event):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().value() - event.angleDelta().y()
        )
        event.accept()

    def closeEvent(self, event):
        # Ensure serial connection used by graph page is closed on exit
        try:
            if hasattr(self, 'graph_page') and self.graph_page is not None:
                try:
                    self.graph_page.close_serial_connection()
                except Exception:
                    pass
        except Exception:
            pass
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    sys.exit(app.exec())

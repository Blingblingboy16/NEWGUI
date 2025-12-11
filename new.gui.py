import sys
import random
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QStackedWidget, QSpacerItem, QSizePolicy, QColorDialog,
    QLineEdit, QToolBar, QComboBox, QDateEdit, QSpinBox, QSlider, QCheckBox, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QDate
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
        # no inline styles, handled by stylesheet
        layout.addWidget(title_label)

        self.body = QVBoxLayout()
        self.body.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.body.setSpacing(20)
        layout.addLayout(self.body)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class MainPage(BasePage):
    def __init__(self, switch):
        super().__init__("Auxora NanoLab Control")

        # Main horizontal layout for two columns
        main_layout = QHBoxLayout()
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left Column - Review Data Section
        data_group = QGroupBox("Review NanoLab Data")
        data_group.setStyleSheet("font-size: 18px; font-weight: bold;")
        data_layout = QVBoxLayout()
        data_layout.setSpacing(20)
        data_layout.setContentsMargins(20, 25, 20, 25)

        # Placeholder for data content
        data_placeholder = QLabel("Data visualization and results will be displayed here.\n\nCurrent status: Connected to NanoLab\nLast update: November 20, 2025 4:16 PM")
        data_placeholder.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        data_placeholder.setStyleSheet("font-size: 14px; padding: 10px;")
        data_layout.addWidget(data_placeholder)

        # Data action buttons
        data_btn_layout = QVBoxLayout()
        data_btn_layout.setSpacing(10)
        view_data_btn = QPushButton("View Experiment Graphing")
        view_data_btn.clicked.connect(lambda: switch("graph"))
        export_data_btn = QPushButton("Export Data")
        clear_data_btn = QPushButton("Clear Data")

        for btn in (view_data_btn, export_data_btn, clear_data_btn):
            style_button(btn)
            data_btn_layout.addWidget(btn)

        data_layout.addLayout(data_btn_layout)
        data_layout.addStretch()
        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

        # Right Column - Adjust Settings Section
        settings_group = QGroupBox("Adjust NanoLab Settings")
        settings_group.setStyleSheet("font-size: 18px; font-weight: bold;")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(20)
        settings_layout.setContentsMargins(20, 25, 20, 25)

        # Connection method dropdown
        connection_layout = QHBoxLayout()
        connection_layout.setSpacing(15)
        connection_label = QLabel("Connection:")
        connection_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["USB Port", "Wireless"])
        self.connection_combo.setMinimumHeight(40)
        connection_layout.addWidget(connection_label)
        connection_layout.addWidget(self.connection_combo)
        connection_layout.addStretch()
        settings_layout.addLayout(connection_layout)

        # Grid of setting buttons
        grid = QGridLayout()
        grid.setSpacing(18)

        buttons = [
            ("Water Pump", "water"),
            ("LED Settings", "led"),
            ("Fan Settings", "fan"),
            ("Camera", "camera"),
            ("Sensor", "sensor"),
            ("Schedule", "schedule"),
        ]

        row, col = 0, 0
        for text, target in buttons:
            btn = QPushButton(text)
            style_button(btn)
            btn.setMinimumHeight(48)
            btn.clicked.connect(lambda _, t=target: switch(t))
            grid.addWidget(btn, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1

        settings_layout.addLayout(grid)
        settings_layout.addStretch()

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # Set stretch factors to make columns equal width
        main_layout.setStretchFactor(data_group, 1)
        main_layout.setStretchFactor(settings_group, 1)

        self.body.addLayout(main_layout)

        # Bottom section with Settings Overview and Send to NanoLab buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        bottom_layout.setContentsMargins(20, 20, 20, 20)

        # Settings Overview button
        overview_btn = QPushButton("Settings Overview")
        overview_btn.clicked.connect(lambda: switch("overview"))
        overview_btn.setStyleSheet("font-size: 16px; color: black; background-color: white; border: 1px solid #a8d5a2; border-radius: 4px; padding: 8px; min-height: 40px;")
        bottom_layout.addWidget(overview_btn)

        # Send to NanoLab button
        send_btn = QPushButton("Send to NanoLab")
        send_btn.clicked.connect(lambda: switch("send"))  # Placeholder - you might want to implement this
        send_btn.setStyleSheet("font-size: 16px; color: black; background-color: white; border: 1px solid #a8d5a2; border-radius: 4px; padding: 8px; min-height: 40px;")
        bottom_layout.addWidget(send_btn)

        # Center the buttons
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.body.addLayout(bottom_layout)

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
        flow_label = QLabel("Flow Rate (L/min):")
        flow_label.setStyleSheet("font-size: 14px;")
        self.flow_spinbox = QSpinBox()
        self.flow_spinbox.setMinimum(0)
        self.flow_spinbox.setMaximum(20)
        self.flow_spinbox.setValue(10)
        flow_layout.addWidget(flow_label)
        flow_layout.addWidget(self.flow_spinbox)
        flow_layout.addStretch()

        self.body.addLayout(flow_layout)

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
        back_btn = QPushButton("Return to Homepage")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

    def apply_water_pump(self):
        main_window = self.parent().parent()
        main_window.water_pump_status = self.pump_toggle.isChecked()
        main_window.water_pump_speed = self.speed_slider.value()
        main_window.water_pump_flow = self.flow_spinbox.value()
        main_window.water_pump_duration = self.duration_spinbox.value()
        main_window.water_pump_interval = self.run_interval_spinbox.value()
        print("Water pump settings applied")

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

        # Color picker
        color_layout = QHBoxLayout()
        color_layout.setSpacing(15)
        color_label = QLabel("Select Color:")
        color_label.setStyleSheet("font-size: 14px;")
        self.color_display = QLabel()
        self.color_display.setFixedSize(50, 50)
        self.color_display.setStyleSheet("background-color: #ffffff; border: 2px solid black;")
        pick_btn = QPushButton("Pick Color")
        pick_btn.clicked.connect(self.pick_color)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_display)
        color_layout.addWidget(pick_btn)
        color_layout.addStretch()

        self.body.addLayout(color_layout)

        # HEX input
        hex_layout = QHBoxLayout()
        hex_layout.setSpacing(15)
        hex_label = QLabel("HEX Color:")
        hex_label.setStyleSheet("font-size: 14px;")
        self.hex_input = QLineEdit("#ffffff")
        self.hex_input.setMaxLength(7)
        hex_layout.addWidget(hex_label)
        hex_layout.addWidget(self.hex_input)
        hex_layout.addStretch()

        self.body.addLayout(hex_layout)

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

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_display.setStyleSheet(f"background-color: {color.name()}; border: 2px solid black;")
            self.hex_input.setText(color.name().upper())

    def apply_led(self):
        main_window = self.parent().parent()
        main_window.led_status = self.led_toggle.isChecked()
        main_window.led_brightness = self.brightness_slider.value()
        main_window.led_color = self.hex_input.text()
        main_window.led_duration = self.duration_spinbox.value()
        main_window.led_interval = self.run_interval_spinbox.value()
        print("LED settings applied")

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
        main_window = self.parent().parent()
        main_window.fan_status = self.fan_toggle.isChecked()
        main_window.fan_intensity = self.intensity_slider.value()
        main_window.fan_duration = self.duration_spinbox.value()
        main_window.fan_interval = self.run_interval_spinbox.value()
        print("Fan settings applied")

class CameraPage(BasePage):
    def __init__(self, switch):
        super().__init__("Camera Settings")

        # Camera status toggle
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        status_label = QLabel("Camera Status:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.camera_toggle = QCheckBox("On/Off")
        self.camera_toggle.setChecked(True)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.camera_toggle)
        status_layout.addStretch()

        self.body.addLayout(status_layout)

        # Resolution dropdown
        res_layout = QHBoxLayout()
        res_layout.setSpacing(15)
        res_label = QLabel("Resolution:")
        res_label.setStyleSheet("font-size: 14px;")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["640x480", "1280x720", "1920x1080", "2560x1440"])
        self.resolution_combo.setCurrentText("1280x720")
        res_layout.addWidget(res_label)
        res_layout.addWidget(self.resolution_combo)
        res_layout.addStretch()

        self.body.addLayout(res_layout)

        # Exposure slider
        exposure_layout = QVBoxLayout()
        exposure_layout.setSpacing(10)
        exposure_label = QLabel("Exposure: 50")
        exposure_label.setStyleSheet("font-size: 14px;")
        self.exposure_slider = QSlider(Qt.Orientation.Horizontal)
        self.exposure_slider.setMinimum(0)
        self.exposure_slider.setMaximum(100)
        self.exposure_slider.setValue(50)
        self.exposure_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.exposure_slider.setTickInterval(10)
        self.exposure_slider.valueChanged.connect(lambda v: exposure_label.setText(f"Exposure: {v}"))

        exposure_layout.addWidget(exposure_label)
        exposure_layout.addWidget(self.exposure_slider)
        self.body.addLayout(exposure_layout)

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
        apply_btn.clicked.connect(self.apply_camera)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

    def apply_camera(self):
        main_window = self.parent().parent()
        main_window.camera_status = self.camera_toggle.isChecked()
        main_window.camera_resolution = self.resolution_combo.currentText()
        main_window.camera_exposure = self.exposure_slider.value()
        main_window.camera_duration = self.duration_spinbox.value()
        main_window.camera_interval = self.run_interval_spinbox.value()
        print("Camera settings applied")

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

        # Temperature threshold
        temp_layout = QHBoxLayout()
        temp_layout.setSpacing(15)
        temp_label = QLabel("Temperature Threshold (°C):")
        temp_label.setStyleSheet("font-size: 14px;")
        self.temp_spinbox = QSpinBox()
        self.temp_spinbox.setMinimum(0)
        self.temp_spinbox.setMaximum(50)
        self.temp_spinbox.setValue(25)
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_spinbox)
        temp_layout.addStretch()

        self.body.addLayout(temp_layout)

        # Humidity threshold
        humidity_layout = QHBoxLayout()
        humidity_layout.setSpacing(15)
        humidity_label = QLabel("Humidity Threshold (%):")
        humidity_label.setStyleSheet("font-size: 14px;")
        self.humidity_spinbox = QSpinBox()
        self.humidity_spinbox.setMinimum(0)
        self.humidity_spinbox.setMaximum(100)
        self.humidity_spinbox.setValue(60)
        humidity_layout.addWidget(humidity_label)
        humidity_layout.addWidget(self.humidity_spinbox)
        humidity_layout.addStretch()

        self.body.addLayout(humidity_layout)

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
        apply_btn.clicked.connect(self.apply_sensor)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

    def apply_sensor(self):
        main_window = self.parent().parent()
        main_window.sensor_status = self.sensor_toggle.isChecked()
        main_window.sensor_reading_interval = self.interval_spinbox.value()
        main_window.sensor_temp_threshold = self.temp_spinbox.value()
        main_window.sensor_humidity_threshold = self.humidity_spinbox.value()
        main_window.sensor_duration = self.duration_spinbox.value()
        main_window.sensor_interval = self.run_interval_spinbox.value()
        print("Sensor settings applied")

class SettingsOverviewPage(BasePage):
    def __init__(self, switch, main_window):
        super().__init__("Settings Overview")

        # Get main window reference
        self.main_window = main_window

        # Back to Main button at the top
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_btn = QPushButton("Back to Main Page")
        back_btn.clicked.connect(lambda: switch("main"))
        back_btn.setStyleSheet("font-size: 16px; padding: 12px 24px; background-color: #2f4f2d; border: none; border-radius: 6px;")
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

        # LED Settings Overview
        led_group = QGroupBox("LED Settings")
        led_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        led_layout = QVBoxLayout()
        led_layout.setSpacing(10)
        led_layout.setContentsMargins(15, 15, 15, 15)

        self.led_labels = []
        led_settings_texts = [
            "Status: On",
            "Brightness: 70%",
            "Color: #FFFFFF",
            "Duration: 300 seconds",
            "Interval: 60 minutes"
        ]

        for text in led_settings_texts:
            setting_label = QLabel(text)
            setting_label.setStyleSheet("font-size: 14px;")
            led_layout.addWidget(setting_label)
            self.led_labels.append(setting_label)

        # Center the edit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_led_btn = QPushButton("Edit LED Settings")
        edit_led_btn.clicked.connect(lambda: switch("led"))
        edit_led_btn.setStyleSheet("font-size: 14px; padding: 10px 20px; background-color: #6bb37a; color: white; border: none; border-radius: 6px;")
        btn_layout.addWidget(edit_led_btn)
        btn_layout.addStretch()
        led_layout.addLayout(btn_layout)

        led_group.setLayout(led_layout)
        overview_layout.addWidget(led_group)

        # Fan Settings Overview
        fan_group = QGroupBox("Fan Settings")
        fan_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        fan_layout = QVBoxLayout()
        fan_layout.setSpacing(10)
        fan_layout.setContentsMargins(15, 15, 15, 15)

        self.fan_labels = []
        fan_settings_texts = [
            "Status: On",
            "Intensity: 75%",
            "Duration: 300 seconds",
            "Interval: 60 minutes"
        ]

        for text in fan_settings_texts:
            setting_label = QLabel(text)
            setting_label.setStyleSheet("font-size: 14px;")
            fan_layout.addWidget(setting_label)
            self.fan_labels.append(setting_label)

        # Center the edit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_fan_btn = QPushButton("Edit Fan Settings")
        edit_fan_btn.clicked.connect(lambda: switch("fan"))
        edit_fan_btn.setStyleSheet("font-size: 14px; padding: 10px 20px; background-color: #6bb37a; color: white; border: none; border-radius: 6px;")
        btn_layout.addWidget(edit_fan_btn)
        btn_layout.addStretch()
        fan_layout.addLayout(btn_layout)

        fan_group.setLayout(fan_layout)
        overview_layout.addWidget(fan_group)

        # Camera Settings Overview
        camera_group = QGroupBox("Camera")
        camera_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        camera_layout = QVBoxLayout()
        camera_layout.setSpacing(10)
        camera_layout.setContentsMargins(15, 15, 15, 15)

        self.camera_labels = []
        camera_settings_texts = [
            "Status: On",
            "Resolution: 1280x720",
            "Exposure: 50",
            "Duration: 300 seconds",
            "Interval: 60 minutes"
        ]

        for text in camera_settings_texts:
            setting_label = QLabel(text)
            setting_label.setStyleSheet("font-size: 14px;")
            camera_layout.addWidget(setting_label)
            self.camera_labels.append(setting_label)

        # Center the edit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        edit_camera_btn = QPushButton("Edit Camera Settings")
        edit_camera_btn.clicked.connect(lambda: switch("camera"))
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
            "Temperature Threshold: 25°C",
            "Humidity Threshold: 60%",
            "Duration: 300 seconds",
            "Interval: 60 minutes"
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

        # Schedule Settings Overview (Placeholder)
        schedule_group = QGroupBox("Schedule")
        schedule_group.setStyleSheet("font-size: 16px; font-weight: bold;")
        schedule_layout = QVBoxLayout()
        schedule_layout.setSpacing(10)
        schedule_layout.setContentsMargins(15, 15, 15, 15)

        schedule_placeholder = QLabel("Schedule Settings will be implemented here.")
        schedule_placeholder.setStyleSheet("font-size: 14px;")
        schedule_layout.addWidget(schedule_placeholder)

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

        # Back button
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))
        self.body.addWidget(back_btn)

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
        self.led_labels[2].setText(f"Color: {self.main_window.led_color.upper()}")
        self.led_labels[3].setText(f"Duration: {self.main_window.led_duration} seconds")
        self.led_labels[4].setText(f"Interval: {self.main_window.led_interval} minutes")

        # Update fan labels
        self.fan_labels[0].setText(f"Status: {'On' if self.main_window.fan_status else 'Off'}")
        self.fan_labels[1].setText(f"Intensity: {self.main_window.fan_intensity}%")
        self.fan_labels[2].setText(f"Duration: {self.main_window.fan_duration} seconds")
        self.fan_labels[3].setText(f"Interval: {self.main_window.fan_interval} minutes")

        # Update camera labels
        self.camera_labels[0].setText(f"Status: {'On' if self.main_window.camera_status else 'Off'}")
        self.camera_labels[1].setText(f"Resolution: {self.main_window.camera_resolution}")
        self.camera_labels[2].setText(f"Exposure: {self.main_window.camera_exposure}")
        self.camera_labels[3].setText(f"Duration: {self.main_window.camera_duration} seconds")
        self.camera_labels[4].setText(f"Interval: {self.main_window.camera_interval} minutes")

        # Update sensor labels
        self.sensor_labels[0].setText(f"Status: {'On' if self.main_window.sensor_status else 'Off'}")
        self.sensor_labels[1].setText(f"Reading Interval: {self.main_window.sensor_reading_interval} minutes")
        self.sensor_labels[2].setText(f"Temperature Threshold: {self.main_window.sensor_temp_threshold}°C")
        self.sensor_labels[3].setText(f"Humidity Threshold: {self.main_window.sensor_humidity_threshold}%")
        self.sensor_labels[4].setText(f"Duration: {self.main_window.sensor_duration} seconds")
        self.sensor_labels[5].setText(f"Interval: {self.main_window.sensor_interval} minutes")

class DataGraphPage(BasePage):
    def __init__(self, switch):
        super().__init__("NanoLab Data Visualization")

        # Create graph canvas
        self.graph = GraphCanvas(self)

        # Manual data entry
        manual_layout = QHBoxLayout()
        manual_layout.setSpacing(15)
        manual_layout.addWidget(QLabel("Length of your plant (cm):"))
        self.length_input = QLineEdit()
        self.length_input.setPlaceholderText("Enter plant length")
        manual_layout.addWidget(self.length_input)
        add_btn = QPushButton("Add Data Point")
        add_btn.clicked.connect(self.add_data_point)
        manual_layout.addWidget(add_btn)
        self.body.addLayout(manual_layout)

        # Interval display
        self.interval_label = QLabel("Last interval: N/A")
        self.interval_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.body.addWidget(self.interval_label)

        # Run experiment button
        run_btn = QPushButton("Load Experiment Data")
        style_button(run_btn)
        run_btn.clicked.connect(self.update_graph)

        # Buttons layout (similar to other pages)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_settings)
        apply_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)

        # Add widgets to layout
        self.body.addWidget(self.graph)
        self.body.addWidget(run_btn)
        self.body.addLayout(btn_layout)

        # Initialize manual data storage
        import time
        self.start_time = time.time()
        self.times = []
        self.lengths = []
        self.csv_filename = "experiment_data_manual.csv"

        # Create CSV header if not exists
        try:
            with open(self.csv_filename, "r") as f:
                pass
        except FileNotFoundError:
            with open(self.csv_filename, "w", newline="") as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["Time (minutes)", "Plant Length (cm)"])

    def update_graph(self):
        # Read experiment data from CSV files
        experiment_data = []

        # Try to read experiment_data_Graph_#1.csv
        try:
            with open("experiment_data_Graph_#1.csv", "r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                data1 = [(float(row[0]), float(row[1])) for row in reader]
                experiment_data.append(("Experiment 1", data1, 'b-', 'o'))
        except FileNotFoundError:
            print("experiment_data_Graph_#1.csv not found")
        except Exception as e:
            print(f"Error reading experiment_data_Graph_#1.csv: {e}")

        # Try to read experiment_data_Graph_#2.csv
        try:
            with open("experiment_data_Graph_#2.csv", "r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                data2 = [(float(row[0]), float(row[1])) for row in reader]
                experiment_data.append(("Experiment 2", data2, 'r-', 's'))
        except FileNotFoundError:
            print("experiment_data_Graph_#2.csv not found")
        except Exception as e:
            print(f"Error reading experiment_data_Graph_#2.csv: {e}")

        # Plot the data
        self.graph.ax.clear()

        has_data = False
        if experiment_data:
            for name, data, color, marker in experiment_data:
                if data:
                    times, lengths = zip(*data)
                    self.graph.ax.plot(times, lengths, color, linewidth=2, markersize=6, marker=marker, label=name)
                    has_data = True

        # Plot manual data
        if self.lengths:
            self.graph.ax.plot(self.times, self.lengths, 'g-', linewidth=2, markersize=6, marker='^', label="Manual Data")
            has_data = True

        if has_data:
            self.graph.ax.set_title("NanoLab Plant Growth Experiments", fontsize=16, fontweight='bold')
            self.graph.ax.set_xlabel("Time (minutes)", fontsize=14)
            self.graph.ax.set_ylabel("Plant Length (cm)", fontsize=14)
            self.graph.ax.grid(True, alpha=0.3)
            self.graph.ax.legend()
        else:
            # Fallback if no data found
            self.graph.ax.text(0.5, 0.5, "No experiment data found.\nPlease ensure CSV files are in the current directory.",
                              horizontalalignment='center', verticalalignment='center', transform=self.graph.ax.transAxes)

        self.graph.draw()   # refresh canvas

    def add_data_point(self):
        try:
            length = float(self.length_input.text())
            if length < 0:
                return
        except ValueError:
            return

        import time
        elapsed_minutes = round((time.time() - self.start_time) / 60, 2)
        self.times.append(elapsed_minutes)
        self.lengths.append(length)

        with open(self.csv_filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([elapsed_minutes, length])

        # Update interval display
        if len(self.times) > 1:
            last_interval = self.times[-1] - self.times[-2]
            self.interval_label.setText(f"Last interval: {last_interval:.2f} minutes")
        else:
            self.interval_label.setText("Last interval: N/A (first point)")

        self.length_input.clear()
        self.update_graph()

    def apply_settings(self):
        # Save manual data settings or confirm
        print("Graph settings applied - manual data saved")

class SchedulePage(BasePage):
    def __init__(self, switch):
        super().__init__("Schedule Settings")

        # Placeholder content
        label = QLabel("Schedule Settings will be implemented here.")
        self.body.addWidget(label)

        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))
        self.body.addWidget(back_btn)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auxora NanoLab Control")
        self.setGeometry(100, 100, 1200, 800)

        # Navigation history
        self.page_history = []
        self.current_history_index = -1

        # Settings storage
        self.water_pump_status = True
        self.water_pump_speed = 50
        self.water_pump_flow = 10
        self.water_pump_duration = 300
        self.water_pump_interval = 60

        self.led_status = True
        self.led_brightness = 70
        self.led_color = "#ffffff"
        self.led_duration = 300
        self.led_interval = 60

        self.fan_status = True
        self.fan_intensity = 75
        self.fan_duration = 300
        self.fan_interval = 60

        self.camera_status = True
        self.camera_resolution = "1280x720"
        self.camera_exposure = 50
        self.camera_duration = 300
        self.camera_interval = 60

        self.sensor_status = True
        self.sensor_reading_interval = 5
        self.sensor_temp_threshold = 25
        self.sensor_humidity_threshold = 60
        self.sensor_duration = 300
        self.sensor_interval = 60

        self.stack = QStackedWidget()
        self.stack.addWidget(MainPage(self.switch_page))
        self.stack.addWidget(WaterPumpPage(self.switch_page))
        self.stack.addWidget(LEDSettingsPage(self.switch_page))
        self.stack.addWidget(FanSettingsPage(self.switch_page))
        self.stack.addWidget(CameraPage(self.switch_page))
        self.stack.addWidget(SensorPage(self.switch_page))
        self.stack.addWidget(DataGraphPage(self.switch_page))
        self.stack.addWidget(SchedulePage(self.switch_page))
        self.stack.addWidget(SettingsOverviewPage(self.switch_page, self))

        # Navigation bar
        nav_toolbar = self.addToolBar("Navigation")
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        style_button(self.back_btn)
        self.forward_btn = QPushButton("Forward →")
        self.forward_btn.clicked.connect(self.go_forward)
        style_button(self.forward_btn)
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        style_button(self.save_btn)

        spacer_left = QWidget()
        spacer_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        nav_toolbar.addWidget(spacer_left)

        nav_toolbar.addWidget(self.back_btn)
        nav_toolbar.addSeparator()
        nav_toolbar.addWidget(self.forward_btn)
        nav_toolbar.addSeparator()
        nav_toolbar.addWidget(self.save_btn)

        spacer_right = QWidget()
        spacer_right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        nav_toolbar.addWidget(spacer_right)

        self.update_navigation_buttons()

        self.setCentralWidget(self.stack)

        # Global stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {LIGHT_BG}; }}
            QLabel {{ font-size: 16px; color: {TEXT_LIGHT}; }}
            #titleLabel {{ font-size: 28px; font-weight: bold; color: {GREEN_DARK}; }}
            QPushButton {{ background-color: {GREEN}; color: {TEXT_LIGHT}; border: none; border-radius: 8px; font-size: 16px; }}
            QPushButton:hover {{ background-color: {GREEN_DARK}; }}
            QComboBox {{ background-color: white; border: 1px solid {GREEN}; border-radius: 4px; padding: 8px; }}
            QGroupBox {{ font-weight: bold; border: 2px solid {GREEN_DARK}; border-radius: 8px; margin-top: 1ex; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 10px 0 10px; }}
        """)

    def switch_page(self, page_name):
        # Map page names to indices
        page_map = {
            "main": 0,
            "water": 1,
            "led": 2,
            "fan": 3,
            "camera": 4,
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

    def go_back(self):
        if self.current_history_index > 0:
            self.current_history_index -= 1
            self.stack.setCurrentIndex(self.page_history[self.current_history_index])
            self.update_navigation_buttons()

    def go_forward(self):
        if self.current_history_index < len(self.page_history) - 1:
            self.current_history_index += 1
            self.stack.setCurrentIndex(self.page_history[self.current_history_index])
            self.update_navigation_buttons()

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

    def update_navigation_buttons(self):
        self.back_btn.setEnabled(self.current_history_index > 0)
        self.forward_btn.setEnabled(self.current_history_index < len(self.page_history) - 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

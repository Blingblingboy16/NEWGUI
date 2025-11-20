import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QStackedWidget, QSpacerItem, QSizePolicy, QColorDialog,
    QLineEdit, QToolBar, QComboBox, QDateEdit, QSpinBox, QSlider, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

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
        view_data_btn = QPushButton("View Latest Data")
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

        # Send to NanoLab button
        send_btn = QPushButton("Send to NanoLab")
        style_button(send_btn)
        send_btn.setMinimumHeight(45)
        settings_layout.addWidget(send_btn)
        settings_layout.addStretch()

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # Set stretch factors to make columns equal width
        main_layout.setStretchFactor(data_group, 1)
        main_layout.setStretchFactor(settings_group, 1)

        self.body.addLayout(main_layout)

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
        back_btn = QPushButton("Back to Main")
        style_button(back_btn)
        back_btn.clicked.connect(lambda: switch("main"))

        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(back_btn)
        self.body.addLayout(btn_layout)

    def apply_water_pump(self):
        # Placeholder for applying settings
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
        # Placeholder for applying settings
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

        # Speed slider
        speed_layout = QVBoxLayout()
        speed_layout.setSpacing(10)
        speed_label = QLabel("Fan Speed: 75%")
        speed_label.setStyleSheet("font-size: 14px;")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(75)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(lambda v: speed_label.setText(f"Fan Speed: {v}%"))

        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        self.body.addLayout(speed_layout)

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
        # Placeholder for applying settings
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
        # Placeholder for applying settings
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
        # Placeholder for applying settings
        print("Sensor settings applied")

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

        self.stack = QStackedWidget()
        self.stack.addWidget(MainPage(self.switch_page))
        self.stack.addWidget(WaterPumpPage(self.switch_page))
        self.stack.addWidget(LEDSettingsPage(self.switch_page))
        self.stack.addWidget(FanSettingsPage(self.switch_page))
        self.stack.addWidget(CameraPage(self.switch_page))
        self.stack.addWidget(SensorPage(self.switch_page))
        self.stack.addWidget(SchedulePage(self.switch_page))

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
        if page_name == "main":
            self.stack.setCurrentIndex(0)
        elif page_name == "water":
            self.stack.setCurrentIndex(1)
        elif page_name == "led":
            self.stack.setCurrentIndex(2)
        elif page_name == "fan":
            self.stack.setCurrentIndex(3)
        elif page_name == "camera":
            self.stack.setCurrentIndex(4)
        elif page_name == "sensor":
            self.stack.setCurrentIndex(5)
        elif page_name == "schedule":
            self.stack.setCurrentIndex(6)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QStackedWidget, QSpacerItem, QSizePolicy, QColorDialog,
    QLineEdit, QToolBar, QComboBox, QDateEdit, QSpinBox, QSlider
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


class WelcomePage(BasePage):
    def __init__(self, switch):
        super().__init__("Welcome to Auxora Nanolabs")

        review_btn = QPushButton("Review Data")
        settings_btn = QPushButton("Adjust NanoLab Settings")

        for b in (review_btn, settings_btn):
            style_button(b)

        review_btn.clicked.connect(lambda: switch("data"))
        settings_btn.clicked.connect(lambda: switch("settings_menu"))

        # Set fixed width for buttons to make them consistent
        review_btn.setFixedWidth(350)
        settings_btn.setFixedWidth(350)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(review_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(20)

        self.body.addLayout(layout)


class SettingsMenuPage(BasePage):
    def __init__(self, switch):
        super().__init__("Adjust NanoLab Settings")

        # Connection method dropdown
        connection_layout = QHBoxLayout()
        connection_layout.setSpacing(15)
        connection_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        connection_label = QLabel("Arduino Connection Method:")
        connection_label.setStyleSheet("font-size: 15px; font-weight: 600;")
        
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["USB Port", "Wireless"])
        self.connection_combo.setMinimumWidth(200)
        self.connection_combo.setMinimumHeight(40)
        self.connection_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        
        connection_layout.addWidget(connection_label)
        connection_layout.addWidget(self.connection_combo)
        
        self.body.addLayout(connection_layout)
        self.body.addSpacing(20)

        grid = QGridLayout()
        grid.setSpacing(18)

        buttons = [
            ("Data Results", "data"),
            ("Water Pump Settings", "water"),
            ("LED Settings", "led"),
            ("Fan Settings", "fan"),
            ("Camera Settings", "camera"),
            ("Atmospheric Sensor", "sensor"),
        ]

        row, col = 0, 0
        for text, target in buttons:
            btn = QPushButton(text)
            style_button(btn)
            btn.setMinimumHeight(48)
            btn.clicked.connect(lambda _, t=target: switch(t))
            grid.addWidget(btn, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        self.body.addLayout(grid)

        send_btn = QPushButton("Send to your NanoLab")
        style_button(send_btn)
        send_btn.setMinimumHeight(45)
        self.body.addWidget(send_btn, alignment=Qt.AlignmentFlag.AlignRight)


class LEDSettingsPage(BasePage):
    def __init__(self):
        super().__init__("LED Settings")

        self.current_color = QColor("#ffffff")
        
        # Description and color button in top row
        top_row = QHBoxLayout()
        top_row.setSpacing(20)
        
        desc_label = QLabel("Configure LED color and operation parameters")
        desc_label.setStyleSheet("font-size: 14px;")
        
        # Button to open color picker dialog in top right
        choose_btn = QPushButton("Choose LED Color")
        style_button(choose_btn)
        choose_btn.setFixedWidth(180)
        choose_btn.clicked.connect(self.open_color_picker)
        
        top_row.addWidget(desc_label)
        top_row.addStretch()
        top_row.addWidget(choose_btn)
        
        self.body.addLayout(top_row)
        self.body.addSpacing(25)
        
        # Container for all sliders with fixed width
        sliders_container = QWidget()
        sliders_container.setFixedWidth(650)
        sliders_layout = QVBoxLayout(sliders_container)
        sliders_layout.setSpacing(25)
        
        # LED Duration Slider
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(15)
        
        duration_label = QLabel("Run Duration (hours):")
        duration_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        duration_label.setFixedWidth(230)
        
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setMinimum(1)
        self.duration_slider.setMaximum(24)
        self.duration_slider.setValue(12)
        self.duration_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.duration_slider.setTickInterval(2)
        
        self.duration_value_label = QLabel("12")
        self.duration_value_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.duration_value_label.setFixedWidth(30)
        self.duration_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_slider)
        duration_layout.addWidget(self.duration_value_label)
        
        sliders_layout.addLayout(duration_layout)
        
        # Run Frequency Slider
        frequency_layout = QHBoxLayout()
        frequency_layout.setSpacing(15)
        
        frequency_label = QLabel("Run Frequency (times/day):")
        frequency_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        frequency_label.setFixedWidth(230)
        
        self.frequency_slider = QSlider(Qt.Orientation.Horizontal)
        self.frequency_slider.setMinimum(1)
        self.frequency_slider.setMaximum(24)
        self.frequency_slider.setValue(2)
        self.frequency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.frequency_slider.setTickInterval(2)
        
        self.frequency_value_label = QLabel("2")
        self.frequency_value_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.frequency_value_label.setFixedWidth(30)
        self.frequency_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        frequency_layout.addWidget(frequency_label)
        frequency_layout.addWidget(self.frequency_slider)
        frequency_layout.addWidget(self.frequency_value_label)
        
        sliders_layout.addLayout(frequency_layout)
        
        # Interval Slider
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(15)
        
        interval_label = QLabel("Interval (hours):")
        interval_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        interval_label.setFixedWidth(230)
        
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(1)
        self.interval_slider.setMaximum(24)
        self.interval_slider.setValue(12)
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.interval_slider.setTickInterval(2)
        
        self.interval_value_label = QLabel("12")
        self.interval_value_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.interval_value_label.setFixedWidth(30)
        self.interval_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.interval_value_label)
        
        sliders_layout.addLayout(interval_layout)
        
        self.body.addWidget(sliders_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.body.addSpacing(20)
        
        # Summary Information
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.summary_label.setStyleSheet("font-size: 13px; font-style: italic; color: #666;")
        self.summary_label.setWordWrap(True)
        self.update_summary()
        self.body.addWidget(self.summary_label)
        self.body.addSpacing(20)
        
        # Connect value changes
        self.duration_slider.valueChanged.connect(self.update_duration_label)
        self.frequency_slider.valueChanged.connect(self.update_frequency_label)
        self.interval_slider.valueChanged.connect(self.update_interval_label)
        
        self.duration_slider.valueChanged.connect(self.update_summary)
        self.frequency_slider.valueChanged.connect(self.update_summary)
        self.interval_slider.valueChanged.connect(self.update_summary)

        # Save button
        save_btn = QPushButton("Save to Settings")
        style_button(save_btn)
        save_btn.setFixedWidth(250)
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white; border-radius: 12px;")
        save_btn.clicked.connect(self.save_settings)
        self.body.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def open_color_picker(self):
        dlg = QColorDialog(self.current_color, self)
        dlg.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        dlg.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)

        if dlg.exec():
            color = dlg.currentColor()
            self.current_color = color
            self.update_ui_color(color)

    def update_ui_color(self, color: QColor):
        hex_code = color.name()
        self.preview.setStyleSheet(f"background-color: {hex_code}; border-radius: 10px; border: 2px solid #aaa;")
    
    def update_duration_label(self, value):
        self.duration_value_label.setText(str(value))
    
    def update_frequency_label(self, value):
        self.frequency_value_label.setText(str(value))
    
    def update_interval_label(self, value):
        self.interval_value_label.setText(str(value))
    
    def update_summary(self):
        """Update the summary information display"""
        duration = self.duration_slider.value()
        frequency = self.frequency_slider.value()
        interval = self.interval_slider.value()
        
        total_runtime = duration * frequency
        summary_text = f"💡 Total daily runtime: {total_runtime} hours  |  ⏱️ Interval: {interval} hours"
        self.summary_label.setText(summary_text)
    
    def save_settings(self):
        """Save the LED settings"""
        color = self.current_color.name()
        duration = self.duration_slider.value()
        frequency = self.frequency_slider.value()
        interval = self.interval_slider.value()
        print(f"LED Settings: Color={color}, Duration={duration}h, Frequency={frequency}x/day, Interval={interval}h")


class SimplePage(BasePage):
    def __init__(self, title):
        super().__init__(title)
        note = QLabel(f"This is the {title} page.")
        note.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.body.addWidget(note)


class AboutPage(BasePage):
    def __init__(self):
        super().__init__("About Auxora Nanolabs")
        
        info_text = QLabel(
            "Auxora Nanolabs Control Panel\n\n"
            "Version 7.0\n\n"
            "A modern interface for controlling and monitoring\n"
            "your NanoLab system with Arduino integration.\n\n"
            "The Auxora NanoLab was modified by:\n"
            "Savannah Finn and Alexandria Tuell"
        )
        info_text.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        info_text.setStyleSheet("font-size: 15px; line-height: 1.6;")
        
        self.body.addWidget(info_text)


class StoragePage(BasePage):
    def __init__(self):
        super().__init__("Storage Settings")
        
        storage_label = QLabel("Manage your data storage and export settings")
        storage_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        export_btn = QPushButton("Export Data")
        clear_btn = QPushButton("Clear Storage")
        
        for btn in (export_btn, clear_btn):
            style_button(btn)
            btn.setFixedWidth(250)
        
        self.body.addWidget(storage_label)
        self.body.addSpacing(20)
        self.body.addWidget(export_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.body.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignHCenter)


class SchedulePage(BasePage):
    def __init__(self):
        super().__init__("Project Schedule")
        
        # Description
        desc_label = QLabel("Select the start and end dates for your NanoLab project")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        desc_label.setStyleSheet("font-size: 15px; margin-bottom: 10px;")
        self.body.addWidget(desc_label)
        self.body.addSpacing(10)
        
        # Start Date Section
        start_container = QVBoxLayout()
        start_container.setSpacing(10)
        start_container.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        start_label = QLabel("Project Start Date:")
        start_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        start_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setMinimumHeight(45)
        self.start_date.setMinimumWidth(250)
        self.start_date.setDisplayFormat("MMMM dd, yyyy")
        self.start_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_date.setCursor(Qt.CursorShape.PointingHandCursor)
        
        start_container.addWidget(start_label)
        start_container.addWidget(self.start_date, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.body.addLayout(start_container)
        self.body.addSpacing(20)
        
        # End Date Section
        end_container = QVBoxLayout()
        end_container.setSpacing(10)
        end_container.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        end_label = QLabel("Project End Date:")
        end_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        end_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(30))
        self.end_date.setMinimumHeight(45)
        self.end_date.setMinimumWidth(250)
        self.end_date.setDisplayFormat("MMMM dd, yyyy")
        self.end_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.end_date.setCursor(Qt.CursorShape.PointingHandCursor)
        
        end_container.addWidget(end_label)
        end_container.addWidget(self.end_date, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.body.addLayout(end_container)
        self.body.addSpacing(30)
        
        # Project duration display
        self.duration_label = QLabel()
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.duration_label.setStyleSheet("font-size: 14px; font-style: italic; color: #666;")
        self.update_duration()
        self.body.addWidget(self.duration_label)
        self.body.addSpacing(20)
        
        # Connect date changes to update duration
        self.start_date.dateChanged.connect(self.update_duration)
        self.end_date.dateChanged.connect(self.update_duration)
        
        # Save button
        save_btn = QPushButton("Save Project Schedule")
        style_button(save_btn)
        save_btn.setFixedWidth(300)
        save_btn.setMinimumHeight(50)
        save_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white; border-radius: 12px; padding: 12px 24px;")
        save_btn.clicked.connect(self.save_schedule)
        self.body.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        
    def update_duration(self):
        """Calculate and display project duration"""
        start = self.start_date.date()
        end = self.end_date.date()
        days = start.daysTo(end)
        
        if days < 0:
            self.duration_label.setText("⚠️ End date must be after start date")
            self.duration_label.setStyleSheet("font-size: 14px; font-style: italic; color: #d32f2f;")
        else:
            self.duration_label.setText(f"Project Duration: {days} days")
            self.duration_label.setStyleSheet("font-size: 14px; font-style: italic; color: #666;")
    
    def save_schedule(self):
        """Save the project schedule (placeholder for future implementation)"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        # Future: Save to database or file
        print(f"Schedule saved: {start} to {end}")


class WaterPumpSettingsPage(BasePage):
    def __init__(self):
        super().__init__("Water Pump Settings")
        
        # Description
        desc_label = QLabel("Configure water pump operation parameters")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        desc_label.setStyleSheet("font-size: 14px;")
        self.body.addWidget(desc_label)
        self.body.addSpacing(25)
        
        # Container for all sliders with fixed width
        sliders_container = QWidget()
        sliders_container.setFixedWidth(650)
        sliders_layout = QVBoxLayout(sliders_container)
        sliders_layout.setSpacing(25)
        
        # Pump Duration Slider
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(15)
        
        duration_label = QLabel("Run Duration (seconds):")
        duration_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        duration_label.setFixedWidth(230)
        
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setMinimum(1)
        self.duration_slider.setMaximum(300)  # Max 5 minutes
        self.duration_slider.setValue(30)
        self.duration_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.duration_slider.setTickInterval(30)
        
        self.duration_value_label = QLabel("30")
        self.duration_value_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.duration_value_label.setFixedWidth(30)
        self.duration_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_slider)
        duration_layout.addWidget(self.duration_value_label)
        
        sliders_layout.addLayout(duration_layout)
        
        # Run Frequency Slider
        frequency_layout = QHBoxLayout()
        frequency_layout.setSpacing(15)
        
        frequency_label = QLabel("Run Frequency (times/day):")
        frequency_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        frequency_label.setFixedWidth(230)
        
        self.frequency_slider = QSlider(Qt.Orientation.Horizontal)
        self.frequency_slider.setMinimum(1)
        self.frequency_slider.setMaximum(24)
        self.frequency_slider.setValue(4)
        self.frequency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.frequency_slider.setTickInterval(2)
        
        self.frequency_value_label = QLabel("4")
        self.frequency_value_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.frequency_value_label.setFixedWidth(30)
        self.frequency_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        frequency_layout.addWidget(frequency_label)
        frequency_layout.addWidget(self.frequency_slider)
        frequency_layout.addWidget(self.frequency_value_label)
        
        sliders_layout.addLayout(frequency_layout)
        
        # Interval Slider
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(15)
        
        interval_label = QLabel("Interval (hours):")
        interval_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        interval_label.setFixedWidth(230)
        
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(1)
        self.interval_slider.setMaximum(24)
        self.interval_slider.setValue(6)  # Default 6 hours
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.interval_slider.setTickInterval(2)
        
        self.interval_value_label = QLabel("6")
        self.interval_value_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.interval_value_label.setFixedWidth(30)
        self.interval_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.interval_value_label)
        
        sliders_layout.addLayout(interval_layout)
        
        self.body.addWidget(sliders_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.body.addSpacing(20)
        
        # Summary Information
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.summary_label.setStyleSheet("font-size: 13px; font-style: italic; color: #666;")
        self.summary_label.setWordWrap(True)
        self.update_summary()
        self.body.addWidget(self.summary_label)
        self.body.addSpacing(20)
        
        # Connect value changes
        self.duration_slider.valueChanged.connect(self.update_duration_label)
        self.frequency_slider.valueChanged.connect(self.update_frequency_label)
        self.interval_slider.valueChanged.connect(self.update_interval_label)
        
        self.duration_slider.valueChanged.connect(self.update_summary)
        self.frequency_slider.valueChanged.connect(self.update_summary)
        self.interval_slider.valueChanged.connect(self.update_summary)
        
        # Save button
        save_btn = QPushButton("Save to Settings")
        style_button(save_btn)
        save_btn.setFixedWidth(250)
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white; border-radius: 12px;")
        save_btn.clicked.connect(self.save_settings)
        self.body.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
    
    def update_duration_label(self, value):
        self.duration_value_label.setText(str(value))
    
    def update_frequency_label(self, value):
        self.frequency_value_label.setText(str(value))
    
    def update_interval_label(self, value):
        self.interval_value_label.setText(str(value))
    
    def update_summary(self):
        """Update the summary information display"""
        duration = self.duration_slider.value()
        frequency = self.frequency_slider.value()
        interval = self.interval_slider.value()
        
        # Calculate total daily runtime
        total_runtime = duration * frequency
        hours = total_runtime // 3600
        minutes = (total_runtime % 3600) // 60
        seconds = total_runtime % 60
        
        runtime_str = ""
        if hours > 0:
            runtime_str += f"{hours}h "
        if minutes > 0:
            runtime_str += f"{minutes}m "
        runtime_str += f"{seconds}s"
        
        summary_text = f"💧 Total runtime: {runtime_str.strip()}  |  ⏱️ Interval: {interval} hours"
        self.summary_label.setText(summary_text)
    
    def save_settings(self):
        """Save the water pump settings"""
        duration = self.duration_slider.value()
        frequency = self.frequency_slider.value()
        interval = self.interval_slider.value()
        print(f"Water Pump: Duration={duration}s, Frequency={frequency}x/day, Interval={interval}h")


class SettingsComparisonPage(BasePage):
    def __init__(self):
        super().__init__("Settings Comparison")
        
        # Description
        desc_label = QLabel(
            "This page will allow you to compare settings used on different days.\n"
            "Track and analyze changes in your NanoLab configuration over time."
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        desc_label.setStyleSheet("font-size: 15px; line-height: 1.6;")
        desc_label.setWordWrap(True)
        self.body.addWidget(desc_label)
        self.body.addSpacing(20)
        
        # Placeholder for future functionality
        placeholder_label = QLabel("⚙️ Coming Soon ⚙️")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        placeholder_label.setStyleSheet("font-size: 24px; font-weight: 600; color: #888;")
        self.body.addWidget(placeholder_label)
        self.body.addSpacing(10)
        
        feature_list = QLabel(
            "Future Features:\n\n"
            "• Select specific dates to compare\n"
            "• View side-by-side setting comparisons\n"
            "• Track LED color changes\n"
            "• Monitor pump and sensor settings\n"
            "• Export comparison reports"
        )
        feature_list.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        feature_list.setStyleSheet("font-size: 14px; line-height: 1.8;")
        self.body.addWidget(feature_list)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auxora Nanolabs Control Panel")
        self.setMinimumSize(900, 650)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.history = []
        self.forward_history = []

        self.current_theme = "light"

        self.pages = {
            "welcome": WelcomePage(self.switch_to),
            "settings_menu": SettingsMenuPage(self.switch_to),
            "data": SimplePage("Data Results"),
            "water": WaterPumpSettingsPage(),
            "led": LEDSettingsPage(),
            "fan": SimplePage("Fan Settings"),
            "camera": SimplePage("Camera Settings"),
            "sensor": SimplePage("Atmospheric Sensor"),
            "about": AboutPage(),
            "storage": StoragePage(),
            "schedule": SchedulePage(),
            "settings_comparison": SettingsComparisonPage(),
        }

        for p in self.pages.values():
            self.stack.addWidget(p)

        self.toolbar_setup()
        self.apply_theme()
        self.switch_to("welcome", record=False)

    def toolbar_setup(self):
        toolbar = QToolBar()
        back_btn = QPushButton("← Back")
        forward_btn = QPushButton("→ Forward")
        schedule_btn = QPushButton("Schedule")
        about_btn = QPushButton("About")
        storage_btn = QPushButton("Storage")
        theme_btn = QPushButton("Toggle Theme")

        for btn in (back_btn, forward_btn, schedule_btn, about_btn, storage_btn, theme_btn):
            style_button(btn)

        back_btn.clicked.connect(self.go_back)
        forward_btn.clicked.connect(self.go_forward)
        schedule_btn.clicked.connect(lambda: self.switch_to("schedule"))
        about_btn.clicked.connect(lambda: self.switch_to("about"))
        storage_btn.clicked.connect(lambda: self.switch_to("storage"))
        theme_btn.clicked.connect(self.toggle_theme)

        toolbar.addWidget(back_btn)
        toolbar.addWidget(forward_btn)
        toolbar.addWidget(schedule_btn)
        toolbar.addWidget(about_btn)
        toolbar.addWidget(storage_btn)
        toolbar.addWidget(theme_btn)
        self.addToolBar(toolbar)

    def switch_to(self, name, record=True):
        if record:
            current_idx = self.stack.currentIndex()
            if not self.history or self.history[-1] != current_idx:
                self.history.append(current_idx)
            self.forward_history.clear()
        self.stack.setCurrentWidget(self.pages[name])

    def go_back(self):
        if not self.history:
            return
        idx = self.history.pop()
        self.forward_history.append(self.stack.currentIndex())
        self.stack.setCurrentIndex(idx)

    def go_forward(self):
        if not self.forward_history:
            return
        idx = self.forward_history.pop()
        self.history.append(self.stack.currentIndex())
        self.stack.setCurrentIndex(idx)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        if self.current_theme == "light":
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: #ffffff;
                }}
                QWidget {{
                    background-color: #ffffff;
                    color: {TEXT_LIGHT};
                    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                }}
                QStackedWidget, QStackedWidget > QWidget {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f5f5f5);
                }}
                QPushButton {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 {GREEN}, stop:1 #86b786);
                    color: black;
                    border: none;
                    border-radius: 14px;
                    padding: 14px 24px;
                    font-weight: 600;
                    font-size: 15px;
                    letter-spacing: 0.3px;
                }}
                QPushButton:hover {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #2f4f2d, stop:1 #4b6a44);
                    color: white;
                    transform: translateY(-2px);
                }}
                QPushButton:pressed {{
                    background-color: #2f4f2d;
                    transform: translateY(0px);
                }}
                QLabel#titleLabel {{
                    font-size: 36px;
                    font-weight: 700;
                    margin-bottom: 20px;
                    color: #1a1a1a;
                    letter-spacing: -0.5px;
                }}
                QLabel {{
                    font-size: 14px;
                    color: #333333;
                }}
                QLineEdit {{
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: #333333;
                }}
                QLineEdit:focus {{
                    border: 2px solid {GREEN};
                }}
                QToolBar {{
                    background-color: #f8f8f8;
                    border-bottom: 1px solid #e0e0e0;
                    spacing: 10px;
                    padding: 8px;
                }}
                QComboBox {{
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: #333333;
                }}
                QComboBox:hover {{
                    border: 2px solid {GREEN};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 30px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 6px solid #333333;
                    margin-right: 8px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: white;
                    border: 2px solid {GREEN};
                    border-radius: 8px;
                    selection-background-color: {GREEN};
                    selection-color: black;
                    padding: 5px;
                }}
                QDateEdit {{
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 15px;
                    font-weight: 600;
                    color: #333333;
                }}
                QDateEdit:hover {{
                    border: 2px solid {GREEN};
                }}
                QDateEdit::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    width: 30px;
                    border: none;
                }}
                QDateEdit::down-arrow {{
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 6px solid #333333;
                }}
                QCalendarWidget {{
                    background-color: white;
                    border: 2px solid {GREEN};
                    border-radius: 8px;
                }}
                QCalendarWidget QTableView {{
                    background-color: white;
                    selection-background-color: {GREEN};
                    selection-color: black;
                }}
                QCalendarWidget QToolButton {{
                    background-color: {GREEN};
                    color: black;
                    border-radius: 6px;
                    padding: 5px;
                }}
                QCalendarWidget QToolButton:hover {{
                    background-color: #2f4f2d;
                    color: white;
                }}
                QSpinBox {{
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 15px;
                    font-weight: 600;
                    color: #333333;
                }}
                QSpinBox:hover {{
                    border: 2px solid {GREEN};
                }}
                QSpinBox:focus {{
                    border: 2px solid {GREEN};
                }}
                QSpinBox::up-button {{
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 25px;
                    border-left: 1px solid #e0e0e0;
                    border-bottom: 1px solid #e0e0e0;
                    border-top-right-radius: 8px;
                    background-color: #f5f5f5;
                }}
                QSpinBox::up-button:hover {{
                    background-color: {GREEN};
                }}
                QSpinBox::down-button {{
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 25px;
                    border-left: 1px solid #e0e0e0;
                    border-bottom-right-radius: 8px;
                    background-color: #f5f5f5;
                }}
                QSpinBox::down-button:hover {{
                    background-color: {GREEN};
                }}
                QSpinBox::up-arrow {{
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-bottom: 5px solid #333333;
                    width: 0px;
                    height: 0px;
                }}
                QSpinBox::down-arrow {{
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 5px solid #333333;
                    width: 0px;
                    height: 0px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: #1a1a1a;
                }}
                QWidget {{
                    background-color: #1a1a1a;
                    color: {TEXT_DARK};
                    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                }}
                QStackedWidget, QStackedWidget > QWidget {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #1a1a1a, stop:1 #0d0d0d);
                }}
                QPushButton {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #2f4f2d, stop:1 #4b6a44);
                    color: white;
                    border: none;
                    border-radius: 14px;
                    padding: 14px 24px;
                    font-weight: 600;
                    font-size: 15px;
                    letter-spacing: 0.3px;
                }}
                QPushButton:hover {{
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 {GREEN}, stop:1 #86b786);
                    color: black;
                    transform: translateY(-2px);
                }}
                QPushButton:pressed {{
                    background-color: {GREEN};
                    transform: translateY(0px);
                }}
                QLabel#titleLabel {{
                    font-size: 36px;
                    font-weight: 700;
                    margin-bottom: 20px;
                    color: #ffffff;
                    letter-spacing: -0.5px;
                }}
                QLabel {{
                    font-size: 14px;
                    color: #e0e0e0;
                }}
                QLineEdit {{
                    background-color: #2a2a2a;
                    border: 2px solid #404040;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: #ffffff;
                }}
                QLineEdit:focus {{
                    border: 2px solid {GREEN};
                }}
                QToolBar {{
                    background-color: #252525;
                    border-bottom: 1px solid #404040;
                    spacing: 10px;
                    padding: 8px;
                }}
                QComboBox {{
                    background-color: #2a2a2a;
                    border: 2px solid #404040;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: #ffffff;
                }}
                QComboBox:hover {{
                    border: 2px solid {GREEN};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 30px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 6px solid #ffffff;
                    margin-right: 8px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: #2a2a2a;
                    border: 2px solid {GREEN};
                    border-radius: 8px;
                    selection-background-color: {GREEN};
                    selection-color: black;
                    padding: 5px;
                }}
                QDateEdit {{
                    background-color: #2a2a2a;
                    border: 2px solid #404040;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 15px;
                    font-weight: 600;
                    color: #ffffff;
                }}
                QDateEdit:hover {{
                    border: 2px solid {GREEN};
                }}
                QDateEdit::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    width: 30px;
                    border: none;
                }}
                QDateEdit::down-arrow {{
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 6px solid #ffffff;
                }}
                QCalendarWidget {{
                    background-color: #2a2a2a;
                    border: 2px solid {GREEN};
                    border-radius: 8px;
                }}
                QCalendarWidget QTableView {{
                    background-color: #2a2a2a;
                    color: #ffffff;
                    selection-background-color: {GREEN};
                    selection-color: black;
                }}
                QCalendarWidget QToolButton {{
                    background-color: #2f4f2d;
                    color: white;
                    border-radius: 6px;
                    padding: 5px;
                }}
                QCalendarWidget QToolButton:hover {{
                    background-color: {GREEN};
                    color: black;
                }}
                QCalendarWidget QWidget {{
                    alternate-background-color: #1a1a1a;
                }}
                QSpinBox {{
                    background-color: #2a2a2a;
                    border: 2px solid #404040;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 15px;
                    font-weight: 600;
                    color: #ffffff;
                }}
                QSpinBox:hover {{
                    border: 2px solid {GREEN};
                }}
                QSpinBox:focus {{
                    border: 2px solid {GREEN};
                }}
                QSpinBox::up-button {{
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 25px;
                    border-left: 1px solid #404040;
                    border-bottom: 1px solid #404040;
                    border-top-right-radius: 8px;
                    background-color: #1a1a1a;
                }}
                QSpinBox::up-button:hover {{
                    background-color: {GREEN};
                }}
                QSpinBox::down-button {{
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 25px;
                    border-left: 1px solid #404040;
                    border-bottom-right-radius: 8px;
                    background-color: #1a1a1a;
                }}
                QSpinBox::down-button:hover {{
                    background-color: {GREEN};
                }}
                QSpinBox::up-arrow {{
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-bottom: 5px solid #ffffff;
                    width: 0px;
                    height: 0px;
                }}
                QSpinBox::down-arrow {{
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 5px solid #ffffff;
                    width: 0px;
                    height: 0px;
                }}
            """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

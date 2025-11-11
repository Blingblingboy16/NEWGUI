import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QStackedWidget, QSpacerItem, QSizePolicy, QColorDialog,
    QLineEdit, QToolBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

# ----- COLORS -----
LIGHT_BG = "#f2f7f2"
DARK_BG = "#2c2f2c"
GREEN = "#a8d5a2"
GREEN_DARK = "#2f4f2d"
TEXT_LIGHT = "black"
TEXT_DARK = "white"


class BasePage(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        self.body = QVBoxLayout()
        layout.addLayout(self.body)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class WelcomePage(BasePage):
    def __init__(self, switch):
        super().__init__("Welcome to NanoLab")

        review_btn = QPushButton("Review Data")
        settings_btn = QPushButton("Adjust NanoLab Settings")

        for b in (review_btn, settings_btn):
            b.setMinimumHeight(50)
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {GREEN};
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 18px;
                    color: black;
                }}
                QPushButton:hover {{
                    background-color: {GREEN_DARK};
                    color: white;
                }}
            """)
            b.setCursor(Qt.CursorShape.PointingHandCursor)

        review_btn.clicked.connect(lambda: switch("data"))
        settings_btn.clicked.connect(lambda: switch("settings_menu"))

        layout = QVBoxLayout()
        layout.addWidget(review_btn)
        layout.addWidget(settings_btn)
        layout.setSpacing(20)

        self.body.addLayout(layout)


class SettingsMenuPage(BasePage):
    def __init__(self, switch):
        super().__init__("Adjust NanoLab Settings")

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
            btn.setMinimumHeight(48)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {GREEN};
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 16px;
                    color: black;
                    padding-left: 15px;
                    padding-right: 15px;
                }}
                QPushButton:hover {{
                    background-color: {GREEN_DARK};
                    color: white;
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, t=target: switch(t))
            grid.addWidget(btn, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        self.body.addLayout(grid)

        send_btn = QPushButton("Send to your NanoLab")
        send_btn.setMinimumHeight(45)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN};
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                color: black;
            }}
            QPushButton:hover {{
                background-color: {GREEN_DARK};
                color: white;
            }}
        """)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.body.addWidget(send_btn, alignment=Qt.AlignmentFlag.AlignRight)


class LEDSettingsPage(BasePage):
    def __init__(self):
        super().__init__("LED Settings")

        self.current_color = QColor("#ffffff")

        # Preview color box
        self.preview = QLabel()
        self.preview.setFixedSize(120, 120)
        self.preview.setStyleSheet("background-color: #ffffff; border-radius: 10px; border: 2px solid #aaa;")

        # HEX input label and field
        hex_label = QLabel("Selected Color (HEX):")
        self.hex_input = QLineEdit("#ffffff")
        self.hex_input.setFixedWidth(150)
        self.hex_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hex_input.textChanged.connect(self.hex_changed)

        # Button to open color picker dialog
        choose_btn = QPushButton("Choose Color")
        choose_btn.setMinimumHeight(45)
        choose_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN};
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                color: black;
            }}
            QPushButton:hover {{
                background-color: {GREEN_DARK};
                color: white;
            }}
        """)
        choose_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        choose_btn.clicked.connect(self.open_color_picker)

        # Save button
        save_btn = QPushButton("Save to Settings")
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white;")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Connect this to your saving logic if needed

        # Layout setup
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self.preview)
        layout.addWidget(hex_label)
        layout.addWidget(self.hex_input)
        layout.addWidget(choose_btn)
        layout.addWidget(save_btn)

        self.body.addLayout(layout)

    def open_color_picker(self):
        dlg = QColorDialog(self.current_color, self)
        dlg.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)  # Force wheel mode
        dlg.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)

        if dlg.exec():
            color = dlg.currentColor()
            self.current_color = color
            self.update_ui_color(color)

    def hex_changed(self, text):
        if QColor.isValidColor(text):
            color = QColor(text)
            self.current_color = color
            self.update_ui_color(color)

    def update_ui_color(self, color: QColor):
        hex_code = color.name()
        self.preview.setStyleSheet(f"background-color: {hex_code}; border-radius: 10px; border: 2px solid #aaa;")
        if self.hex_input.text().lower() != hex_code.lower():
            self.hex_input.blockSignals(True)
            self.hex_input.setText(hex_code)
            self.hex_input.blockSignals(False)


class SimplePage(BasePage):
    def __init__(self, title):
        super().__init__(title)
        note = QLabel(f"This is the {title} page.")
        note.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.body.addWidget(note)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NanoLab Control Panel")
        self.setMinimumSize(850, 550)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.history = []
        self.forward_history = []

        self.current_theme = "light"

        self.pages = {
            "welcome": WelcomePage(self.switch_to),
            "settings_menu": SettingsMenuPage(self.switch_to),
            "data": SimplePage("Data Results"),
            "water": SimplePage("Water Pump Settings"),
            "led": LEDSettingsPage(),
            "fan": SimplePage("Fan Settings"),
            "camera": SimplePage("Camera Settings"),
            "sensor": SimplePage("Atmospheric Sensor"),
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
        theme_btn = QPushButton("Toggle Theme")

        back_btn.clicked.connect(self.go_back)
        forward_btn.clicked.connect(self.go_forward)
        theme_btn.clicked.connect(self.toggle_theme)

        toolbar.addWidget(back_btn)
        toolbar.addWidget(forward_btn)
        toolbar.addWidget(theme_btn)
        self.addToolBar(toolbar)

    def switch_to(self, name, record=True):
        if record:
            # Prevent duplicate consecutive history entries
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
                background-color: {LIGHT_BG};
                color: {TEXT_LIGHT};
                QPushButton {{
                    background-color: {GREEN};
                    color: black;
                }}
                QPushButton:hover {{
                    background-color: {GREEN_DARK};
                    color: white;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                background-color: {DARK_BG};
                color: {TEXT_DARK};
                QPushButton {{
                    background-color: {GREEN_DARK};
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: {GREEN};
                    color: black;
                }}
            """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

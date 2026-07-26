import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox,
    QRadioButton, QButtonGroup, QKeySequenceEdit, QMessageBox,
    QTabWidget, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon
from pynput import mouse, keyboard
import threading

class AstaAutoclicker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asta - Autoclicker")
        self.setGeometry(100, 100, 500, 600)
        
        # Configuration
        self.config_file = "asta_config.json"
        self.config = self.load_config()
        
        # State variables
        self.is_clicking = False
        self.click_thread = None
        self.mouse_controller = mouse.Controller()
        self.listener = None
        
        # Click settings
        self.click_interval = self.config.get("click_interval", 0.1)
        self.click_button = self.config.get("click_button", "left")
        self.mode = self.config.get("mode", "toggle")  # toggle or hold
        self.toggle_key = self.config.get("toggle_key", "f6")
        self.hold_key = self.config.get("hold_key", "f7")
        
        self.init_ui()
        self.setup_listener()
        
    def load_config(self):
        """Load configuration from file if exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            "click_interval": self.click_interval,
            "click_button": self.click_button,
            "mode": self.mode,
            "toggle_key": self.toggle_key,
            "hold_key": self.hold_key
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def init_ui(self):
        """Initialize the UI"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("ASTA")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Advanced AutoClicker")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Status label
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Settings Group
        settings_group = QGroupBox("Click Settings")
        settings_layout = QFormLayout()
        
        # Click interval
        interval_layout = QHBoxLayout()
        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setValue(self.click_interval)
        self.interval_spinbox.setMinimum(0.01)
        self.interval_spinbox.setMaximum(10.0)
        self.interval_spinbox.setSingleStep(0.01)
        self.interval_spinbox.setSuffix(" s")
        self.interval_spinbox.valueChanged.connect(self.on_interval_changed)
        settings_layout.addRow("Click Interval:", self.interval_spinbox)
        
        # Click button selection
        button_layout = QHBoxLayout()
        self.button_group = QButtonGroup()
        
        for i, button in enumerate(["Left", "Right", "Middle"]):
            radio = QRadioButton(button)
            self.button_group.addButton(radio, i)
            button_layout.addWidget(radio)
            if button.lower() == self.click_button:
                radio.setChecked(True)
        
        self.button_group.buttonClicked.connect(self.on_button_changed)
        settings_layout.addRow("Mouse Button:", button_layout)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # Mode Group
        mode_group = QGroupBox("Click Mode")
        mode_layout = QVBoxLayout()
        
        self.toggle_radio = QRadioButton("Toggle Mode (Press key to start/stop)")
        self.hold_radio = QRadioButton("Hold Mode (Click while holding key)")
        
        if self.mode == "toggle":
            self.toggle_radio.setChecked(True)
        else:
            self.hold_radio.setChecked(True)
        
        self.toggle_radio.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.toggle_radio)
        mode_layout.addWidget(self.hold_radio)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)
        
        # Keybind Group
        keybind_group = QGroupBox("Keybinds")
        keybind_layout = QFormLayout()
        
        toggle_layout = QHBoxLayout()
        self.toggle_key_label = QLabel(f"Current: {self.toggle_key.upper()}")
        self.toggle_key_button = QPushButton("Set Toggle Key")
        self.toggle_key_button.clicked.connect(self.set_toggle_key)
        toggle_layout.addWidget(self.toggle_key_label)
        toggle_layout.addWidget(self.toggle_key_button)
        keybind_layout.addRow("Toggle Key:", toggle_layout)
        
        hold_layout = QHBoxLayout()
        self.hold_key_label = QLabel(f"Current: {self.hold_key.upper()}")
        self.hold_key_button = QPushButton("Set Hold Key")
        self.hold_key_button.clicked.connect(self.set_hold_key)
        hold_layout.addWidget(self.hold_key_label)
        hold_layout.addWidget(self.hold_key_button)
        keybind_layout.addRow("Hold Key:", hold_layout)
        
        keybind_group.setLayout(keybind_layout)
        main_layout.addWidget(keybind_group)
        
        # Control Buttons
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.start_button.clicked.connect(self.start_clicking)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px;")
        self.stop_button.clicked.connect(self.stop_clicking)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(control_layout)
        
        # Info label
        info_label = QLabel("Use keybinds to control the autoclicker while the app is running.")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
        
        main_layout.addStretch()
        main_widget.setLayout(main_layout)
    
    def on_interval_changed(self, value):
        self.click_interval = value
        self.save_config()
    
    def on_button_changed(self, button):
        buttons = {0: "left", 1: "right", 2: "middle"}
        self.click_button = buttons[self.button_group.id(button)]
        self.save_config()
    
    def on_mode_changed(self):
        self.mode = "toggle" if self.toggle_radio.isChecked() else "hold"
        self.save_config()
    
    def set_toggle_key(self):
        self.get_key_input("toggle")
    
    def set_hold_key(self):
        self.get_key_input("hold")
    
    def get_key_input(self, key_type):
        """Listen for a key press and set it as the keybind"""
        self.listening_for_key = True
        self.key_type = key_type
        
        if key_type == "toggle":
            QMessageBox.information(self, "Set Toggle Key", "Press any key on your keyboard...")
        else:
            QMessageBox.information(self, "Set Hold Key", "Press any key on your keyboard...")
        
        def on_press(key):
            if self.listening_for_key:
                try:
                    key_str = key.char if hasattr(key, 'char') else str(key).replace("Key.", "")
                    if self.key_type == "toggle":
                        self.toggle_key = key_str
                        self.toggle_key_label.setText(f"Current: {key_str.upper()}")
                    else:
                        self.hold_key = key_str
                        self.hold_key_label.setText(f"Current: {key_str.upper()}")
                    self.listening_for_key = False
                    self.save_config()
                    self.setup_listener()  # Restart listener with new keybinds
                except:
                    pass
                return False
        
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
    
    def setup_listener(self):
        """Setup keyboard listener"""
        if self.listener:
            self.listener.stop()
        
        def on_press(key):
            if not self.is_clicking and self.mode == "toggle":
                try:
                    key_str = key.char if hasattr(key, 'char') else str(key).replace("Key.", "")
                    if key_str == self.toggle_key:
                        self.start_clicking()
                except:
                    pass
        
        def on_release(key):
            if self.mode == "hold":
                try:
                    key_str = key.char if hasattr(key, 'char') else str(key).replace("Key.", "")
                    if key_str == self.hold_key and self.is_clicking:
                        self.stop_clicking()
                except:
                    pass
        
        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
    
    def start_clicking(self):
        """Start the autoclicker"""
        if self.is_clicking:
            return
        
        self.is_clicking = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Status: Clicking...")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()
    
    def stop_clicking(self):
        """Stop the autoclicker"""
        self.is_clicking = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Idle")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def click_loop(self):
        """Main clicking loop"""
        buttons = {"left": mouse.Button.left, "right": mouse.Button.right, "middle": mouse.Button.middle}
        button = buttons[self.click_button]
        
        if self.mode == "hold":
            def on_press(key):
                if not self.is_clicking:
                    try:
                        key_str = key.char if hasattr(key, 'char') else str(key).replace("Key.", "")
                        if key_str == self.hold_key:
                            self.is_clicking = True
                    except:
                        pass
            
            hold_listener = keyboard.Listener(on_press=on_press)
            hold_listener.start()
        
        while self.is_clicking:
            self.mouse_controller.click(button)
            import time
            time.sleep(self.click_interval)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.is_clicking = False
        if self.listener:
            self.listener.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AstaAutoclicker()
    window.show()
    sys.exit(app.exec())

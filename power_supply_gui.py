import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QGroupBox,
    QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pyvisa


class PowerSupplyGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keithley 2230G Controller")
        self.setFixedSize(400, 450)

        # Initialize VISA
        self.rm = pyvisa.ResourceManager()
        self.inst = None
        self.output_state = False

        # Simple styling
        self.setStyleSheet("""
            QLineEdit { padding: 5px; }
            QPushButton { padding: 12px; min-height: 30px; }
        """)

        self.init_ui()
        self.load_devices()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title
        title = QLabel("Keithley 2230G Controller")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Connection section
        conn_group = QGroupBox("Connection")
        conn_layout = QVBoxLayout()

        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        device_layout.addWidget(self.device_combo)
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_device)
        device_layout.addWidget(self.connect_btn)
        conn_layout.addLayout(device_layout)

        self.status_label = QLabel("Not connected")
        conn_layout.addWidget(self.status_label)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Control section
        control_group = QGroupBox("Control")
        control_layout = QGridLayout()

        control_layout.addWidget(QLabel("Channel:"), 0, 0)
        self.channel_input = QLineEdit("1")
        self.channel_input.setFixedWidth(50)
        control_layout.addWidget(self.channel_input, 0, 1)

        control_layout.addWidget(QLabel("Voltage Limit (V):"), 1, 0)
        self.voltage_limit_input = QLineEdit("15.0")
        control_layout.addWidget(self.voltage_limit_input, 1, 1)

        control_layout.addWidget(QLabel("Voltage Set (V):"), 2, 0)
        self.voltage_input = QLineEdit("5.0")
        control_layout.addWidget(self.voltage_input, 2, 1)

        control_layout.addWidget(QLabel("Current (A):"), 3, 0)
        self.current_input = QLineEdit("1.0")
        control_layout.addWidget(self.current_input, 3, 1)

        # Buttons with proper spacing and size
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)

        self.set_btn = QPushButton("Apply Settings")
        self.set_btn.clicked.connect(self.set_values)
        self.set_btn.setEnabled(False)
        self.set_btn.setMinimumHeight(40)
        button_layout.addWidget(self.set_btn)

        self.output_btn = QPushButton("Output: OFF")
        self.output_btn.clicked.connect(self.toggle_output)
        self.output_btn.setEnabled(False)
        self.output_btn.setMinimumHeight(40)
        self.output_btn.setStyleSheet(
            "background-color: #ff6b6b; color: white; font-weight: bold; min-height: 40px; padding: 12px;")
        button_layout.addWidget(self.output_btn)

        control_layout.addLayout(button_layout, 4, 0, 1, 2)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        self.setLayout(layout)

    def load_devices(self):
        """Load available VISA devices"""
        try:
            resources = self.rm.list_resources()
            self.device_combo.addItems(resources)
            if not resources:
                self.device_combo.addItem("No devices found")
        except:
            self.device_combo.addItem("No devices found")

    def connect_device(self):
        """Connect to selected device"""
        device = self.device_combo.currentText()
        if device == "No devices found":
            QMessageBox.warning(self, "Error", "No devices available")
            return

        try:
            self.inst = self.rm.open_resource(device)
            idn = self.inst.query("*IDN?").strip()

            self.status_label.setText(f"Connected: {idn.split(',')[0]}")
            self.connect_btn.setText("Connected")
            self.connect_btn.setEnabled(False)
            self.set_btn.setEnabled(True)
            self.output_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def set_values(self):
        """Set voltage and current"""
        if not self.inst:
            return

        try:
            channel = int(self.channel_input.text())
            voltage_limit = float(self.voltage_limit_input.text())
            voltage = float(self.voltage_input.text())
            current = float(self.current_input.text())

            if not (1 <= channel <= 3):
                raise ValueError("Channel must be 1, 2, or 3")
            if voltage_limit <= 0 or voltage < 0 or current < 0:
                raise ValueError("Values must be positive")
            if voltage > voltage_limit:
                raise ValueError("Set voltage cannot exceed voltage limit")

            self.inst.write(f"INST:NSEL {channel}")
            self.inst.write(f"SOUR:VOLT:LIM {voltage_limit}")
            self.inst.write("SOUR:VOLT:LIM:STAT ON")
            self.inst.write(f"SOUR:VOLT {voltage}")
            self.inst.write(f"SOUR:CURR {current}")

            self.status_label.setText(f"Set: CH{channel} V={voltage}V I={current}A (Limit: {voltage_limit}V)")

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def toggle_output(self):
        """Toggle output on/off"""
        if not self.inst:
            return

        try:
            self.output_state = not self.output_state
            self.inst.write(f"OUTP {'ON' if self.output_state else 'OFF'}")

            if self.output_state:
                # Output is ON
                self.output_btn.setText("Output: ON")
                self.output_btn.setStyleSheet(
                    "background-color: #51cf66; color: white; font-weight: bold; min-height: 40px; padding: 12px;")
            else:
                # Output is OFF
                self.output_btn.setText("Output: OFF")
                self.output_btn.setStyleSheet(
                    "background-color: #ff6b6b; color: white; font-weight: bold; min-height: 40px; padding: 12px;")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        """Clean up on close"""
        if self.inst:
            try:
                self.inst.close()
            except:
                pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PowerSupplyGUI()
    window.show()
    sys.exit(app.exec())

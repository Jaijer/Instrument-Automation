# Keithley 2230G Power Supply Controller

A Python GUI application for controlling the Keithley 2230G power supply, developed during an internship at Halliburton for instrument automation.

## Features

- Connect to Keithley 2230G power supply via VISA
- Set voltage limits, output voltage, and current for channels 1-3
- Toggle output on/off with clear visual feedback
- Input validation and error handling
- Simple, clean interface

## Requirements

- Python 3.7+
- PySide6
- PyVISA
- NI-VISA runtime

## Installation

1. Install dependencies:
   \`\`\`bash
   pip install PySide6 pyvisa
   \`\`\`

2. Install NI-VISA runtime from National Instruments

3. Run the application:
   \`\`\`bash
   python simple_power_supply_gui.py
   \`\`\`

## Usage

1. Select your device from the dropdown and click "Connect"
2. Set channel (1-3), voltage limit, voltage, and current
3. Click "Apply Settings" to configure the power supply
4. Use "Output: OFF/ON" button to control power output

## Safety

- Voltage output cannot exceed the set voltage limit
- All inputs are validated before sending to instrument
- Clear visual indication of output state (Red=OFF, Green=ON)

---

*Developed during internship at Halliburton for laboratory instrument automation*

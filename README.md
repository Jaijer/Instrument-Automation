# Keithley 2230G Power Supply Controller

A Python application for controlling the Keithley 2230G power supply, developed during an internship at Halliburton for instrument automation.

## Two Ways to Use

### Option 1: Desktop App (Simple)
- **File**: `power_supply_gui.py`
- Simple desktop window
- Basic controls for all 3 channels

### Option 2: Web App (Advanced)
- **File**: `power_supply_server.py`
- Opens in your web browser
- Real-time voltage graphs
- Better looking interface

## Features

- Connect to Keithley 2230G power supply
- Set voltage limits, output voltage, and current for channels 1-3
- Turn outputs on/off with clear visual feedback
- Input validation and error handling
- **Web version**: Real-time voltage monitoring with graphs

## Requirements

- Python 3.7+
- PySide6 (for desktop app)
- FastAPI & PyVISA (for web app)
- NI-VISA runtime

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install NI-VISA runtime from National Instruments

3. Run the application:
   
   **Desktop App:**
   ```bash
   python power_supply_gui.py
   ```
   
   **Web App:**
   ```bash
   python power_supply_server.py
   ```
   Then open http://localhost:8000 in your browser

## Usage

1. Select your device from the dropdown and click "Connect"
2. Set channel, voltage limit, voltage, and current
3. Click "Apply Settings" to configure the power supply
4. Use ON/OFF buttons to control power output
5. **Web version**: Watch real-time voltage graphs

## Safety

- Voltage output cannot exceed the set voltage limit
- All inputs are validated before sending to instrument
- Clear visual indication of output state (Red=OFF, Green=ON)
- Automatic shutdown of all outputs when disconnecting

---

*Developed during internship at Halliburton for laboratory instrument automation*
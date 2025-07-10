from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import pyvisa
import asyncio
import json
from datetime import datetime, timedelta
import uvicorn
import plotly.graph_objs as go
import plotly.utils
from collections import deque
import threading
import time


# Pydantic models for request/response
class PowerSupplySettings(BaseModel):
    channel: int = Field(..., ge=1, le=3, description="Channel number (1-3)")
    voltage_limit: float = Field(..., ge=0, le=30, description="Voltage limit in V")
    voltage_set: float = Field(..., ge=0, le=30, description="Set voltage in V")
    current: float = Field(..., ge=0, le=5, description="Current limit in A")


class OutputControl(BaseModel):
    state: bool = Field(..., description="Output state (True=ON, False=OFF)")


class DeviceStatus(BaseModel):
    connected: bool
    device_info: Optional[str] = None
    last_settings: Optional[Dict[str, Any]] = None
    output_state: bool = False
    timestamp: str
    current_channel: int = 1


class VoltageReading(BaseModel):
    timestamp: str
    voltage: float
    channel: int


# FastAPI app
app = FastAPI(
    title="Keithley 2230G Remote Controller",
    description="Remote control API for Keithley 2230G Power Supply",
    version="1.0.0"
)

# Global variables
rm = None
instrument = None
device_status = {
    "connected": False,
    "device_info": None,
    "last_settings": {},
    "output_state": False,  # Single output state for all channels
    "timestamp": datetime.now().isoformat(),
    "current_channel": 1
}

# Data storage for plotting (store last 100 readings per channel)
voltage_data = {
    1: deque(maxlen=100),
    2: deque(maxlen=100),
    3: deque(maxlen=100)
}
time_data = {
    1: deque(maxlen=100),
    2: deque(maxlen=100),
    3: deque(maxlen=100)
}

# Background monitoring
monitoring_active = False
monitoring_thread = None


def initialize_visa():
    """Initialize VISA resource manager"""
    global rm
    try:
        rm = pyvisa.ResourceManager()
        return True
    except Exception as e:
        print(f"Failed to initialize VISA: {e}")
        return False


def update_status():
    """Update device status timestamp"""
    global device_status
    device_status["timestamp"] = datetime.now().isoformat()


def check_initial_output_state():
    """Check the current output state of all channels when connecting"""
    global instrument, device_status

    try:
        # Check output state for all channels
        output_states = []
        for channel in [1, 2, 3]:
            instrument.write(f"INST:NSEL {channel}")
            output_str = instrument.query("OUTP?")
            output_states.append(int(output_str.strip()) == 1)

        # If any channel is on, consider the master state as ON
        device_status["output_state"] = any(output_states)
        print(f"Initial output states: CH1={output_states[0]}, CH2={output_states[1]}, CH3={output_states[2]}")
        print(f"Master output state set to: {device_status['output_state']}")

    except Exception as e:
        print(f"Error checking initial output state: {e}")
        device_status["output_state"] = False


def monitor_voltage():
    """Background thread to monitor voltage readings"""
    global monitoring_active, instrument, voltage_data, time_data, device_status

    while monitoring_active:
        try:
            if instrument and device_status["connected"]:
                current_channel = device_status["current_channel"]

                # Select current channel and read voltage
                instrument.write(f"INST:NSEL {current_channel}")
                voltage_str = instrument.query("MEAS:VOLT?")
                voltage = float(voltage_str.strip())

                # Store data
                current_time = datetime.now()
                voltage_data[current_channel].append(voltage)
                time_data[current_channel].append(current_time)

                # Clean old data (keep only last 5 minutes)
                cutoff_time = current_time - timedelta(minutes=5)
                while (time_data[current_channel] and
                       time_data[current_channel][0] < cutoff_time):
                    time_data[current_channel].popleft()
                    voltage_data[current_channel].popleft()

        except Exception as e:
            print(f"Monitoring error: {e}")

        time.sleep(1)  # Read every second


def start_monitoring():
    """Start voltage monitoring thread"""
    global monitoring_active, monitoring_thread
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitor_voltage, daemon=True)
        monitoring_thread.start()


def stop_monitoring():
    """Stop voltage monitoring thread"""
    global monitoring_active
    monitoring_active = False


@app.on_event("startup")
async def startup_event():
    """Initialize VISA on startup"""
    if not initialize_visa():
        print("Warning: VISA initialization failed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    stop_monitoring()


@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Keithley 2230G Remote Control</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .button { padding: 12px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: bold; }
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-danger { background: #dc3545; color: white; }
            .btn-secondary { background: #6c757d; color: white; }
            .btn-warning { background: #ffc107; color: black; }
            input, select { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 3px; width: 120px; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .status.connected { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.disconnected { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .output-on { background: #28a745 !important; }
            .output-off { background: #dc3545 !important; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
            .control-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; align-items: center; }
            .channel-selector { display: flex; gap: 10px; margin: 10px 0; }
            .channel-btn { padding: 8px 16px; border: 2px solid #007bff; background: white; color: #007bff; border-radius: 5px; cursor: pointer; }
            .channel-btn.active { background: #007bff; color: white; }
            .power-controls { display: flex; justify-content: center; margin: 10px 0; }
            .power-btn { padding: 12px 24px; font-size: 14px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; }
            .power-on { background: #28a745; color: white; }
            .power-off { background: #dc3545; color: white; }
            .master-output { text-align: center; }
            #plotDiv { height: 400px; margin: 20px 0; }
            @media (max-width: 600px) { 
                .grid { grid-template-columns: 1fr; }
                .control-grid { grid-template-columns: 1fr 1fr; }
                .power-btn { padding: 10px 20px; font-size: 13px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔌 Keithley 2230G Remote Control</h1>

            <div class="section">
                <h3>Connection</h3>
                <button class="button btn-primary" onclick="scanDevices()">Scan Devices</button>
                <select id="deviceSelect"></select>
                <button class="button btn-success" onclick="connectDevice()">Connect</button>
                <div id="connectionStatus" class="status disconnected">Not Connected</div>
            </div>

            <div class="section master-output">
                <div class="power-controls">
                    <button class="power-btn power-off" id="powerBtn" onclick="togglePower()">
                        <span id="powerBtnText">Turn ON</span>
                    </button>
                </div>
            </div>

            <div class="section">
                <h3>Channel Selection</h3>
                <div class="channel-selector">
                    <button class="channel-btn active" id="ch1-btn" onclick="selectChannel(1)">Channel 1</button>
                    <button class="channel-btn" id="ch2-btn" onclick="selectChannel(2)">Channel 2</button>
                    <button class="channel-btn" id="ch3-btn" onclick="selectChannel(3)">Channel 3</button>
                </div>
                <div id="currentChannelInfo">Configuring Channel: 1</div>
            </div>

            <div class="section">
                <h3>Power Supply Control</h3>
                <div class="control-grid">
                    <label>Voltage Limit (V):</label>
                    <input type="number" id="voltageLimit" value="15.0" step="0.1" min="0" max="30">
                    <label>Voltage Set (V):</label>
                    <input type="number" id="voltageSet" value="5.0" step="0.1" min="0" max="30">
                    <label>Current (A):</label>
                    <input type="number" id="current" value="1.0" step="0.1" min="0" max="5">
                    <button class="button btn-primary" onclick="applySettings()" style="grid-column: span 1;">Apply to Channel</button>
                </div>
            </div>

            <div class="section">
                <h3>Real-time Voltage Monitor</h3>
                <div id="plotDiv"></div>
                <button class="button btn-secondary" onclick="clearPlot()">Clear Plot</button>
            </div>
        </div>

        <script>
            let currentDevice = null;
            let currentChannel = 1;
            let plotUpdateInterval = null;

            async function apiCall(endpoint, method = 'GET', data = null) {
                const options = {
                    method: method,
                    headers: { 'Content-Type': 'application/json' }
                };
                if (data) options.body = JSON.stringify(data);

                try {
                    const response = await fetch(endpoint, options);
                    const result = await response.json();
                    if (!response.ok) throw new Error(result.detail || 'API Error');
                    return result;
                } catch (error) {
                    alert('Error: ' + error.message);
                    throw error;
                }
            }

            function selectChannel(channel) {
                currentChannel = channel;

                // Update UI
                document.querySelectorAll('.channel-btn').forEach(btn => btn.classList.remove('active'));
                document.getElementById(`ch${channel}-btn`).classList.add('active');
                document.getElementById('currentChannelInfo').textContent = `Configuring Channel: ${channel}`;

                // Update server
                if (currentDevice) {
                    apiCall('/api/set-channel', 'POST', { channel: channel });
                }
            }

            async function scanDevices() {
                try {
                    const devices = await apiCall('/api/devices');
                    const select = document.getElementById('deviceSelect');
                    select.innerHTML = '';
                    devices.forEach(device => {
                        const option = document.createElement('option');
                        option.value = device;
                        option.textContent = device;
                        select.appendChild(option);
                    });
                } catch (error) {
                    console.error('Failed to scan devices:', error);
                }
            }

            async function connectDevice() {
                const device = document.getElementById('deviceSelect').value;
                if (!device) {
                    alert('Please select a device first');
                    return;
                }

                try {
                    const result = await apiCall('/api/connect', 'POST', { device_address: device });
                    document.getElementById('connectionStatus').textContent = 'Connected: ' + result.device_info;
                    document.getElementById('connectionStatus').className = 'status connected';
                    currentDevice = device;

                    // Start monitoring and plotting
                    startPlotUpdates();
                    await updatePowerButton();

                } catch (error) {
                    document.getElementById('connectionStatus').textContent = 'Connection Failed';
                    document.getElementById('connectionStatus').className = 'status disconnected';
                }
            }

            async function applySettings() {
                if (!currentDevice) {
                    alert('Please connect to a device first');
                    return;
                }

                const settings = {
                    channel: currentChannel,
                    voltage_limit: parseFloat(document.getElementById('voltageLimit').value),
                    voltage_set: parseFloat(document.getElementById('voltageSet').value),
                    current: parseFloat(document.getElementById('current').value)
                };

                try {
                    await apiCall('/api/settings', 'POST', settings);
                    alert(`Settings applied to Channel ${currentChannel}`);
                } catch (error) {
                    console.error('Failed to apply settings:', error);
                }
            }

            async function togglePower() {
                if (!currentDevice) {
                    alert('Please connect to a device first');
                    return;
                }

                try {
                    const status = await apiCall('/api/status');
                    const isCurrentlyOn = status.output_state;

                    await apiCall('/api/output', 'POST', { 
                        state: !isCurrentlyOn 
                    });

                    await updatePowerButton();

                } catch (error) {
                    console.error('Failed to toggle power:', error);
                }
            }

            async function updatePowerButton() {
                try {
                    const status = await apiCall('/api/status');
                    const isOn = status.output_state;
                    const powerBtn = document.getElementById('powerBtn');
                    const powerBtnText = document.getElementById('powerBtnText');

                    if (isOn) {
                        powerBtn.className = 'power-btn power-on';
                        powerBtnText.textContent = 'Turn OFF';
                    } else {
                        powerBtn.className = 'power-btn power-off';
                        powerBtnText.textContent = 'Turn ON';
                    }
                } catch (error) {
                    console.error('Failed to update power button:', error);
                }
            }

            async function updatePlot() {
                try {
                    const plotData = await apiCall('/api/plot-data');

                    if (plotData.time.length > 0) {
                        const trace = {
                            x: plotData.time,
                            y: plotData.voltage,
                            type: 'scatter',
                            mode: 'lines+markers',
                            name: `Channel ${currentChannel} Voltage`,
                            line: { color: '#007bff', width: 2 },
                            marker: { size: 4 }
                        };

                        const layout = {
                            title: `Real-time Voltage - Channel ${currentChannel}`,
                            xaxis: { 
                                title: 'Time',
                                type: 'date'
                            },
                            yaxis: { 
                                title: 'Voltage (V)',
                                range: [0, 30]
                            },
                            margin: { t: 50, r: 50, b: 50, l: 50 },
                            showlegend: true
                        };

                        Plotly.newPlot('plotDiv', [trace], layout, {responsive: true});
                    }
                } catch (error) {
                    console.error('Failed to update plot:', error);
                }
            }

            function startPlotUpdates() {
                if (plotUpdateInterval) clearInterval(plotUpdateInterval);
                plotUpdateInterval = setInterval(updatePlot, 2000); // Update every 2 seconds
                updatePlot(); // Initial plot
            }

            function clearPlot() {
                if (currentDevice) {
                    apiCall('/api/clear-data', 'POST');
                    Plotly.purge('plotDiv');
                }
            }

            // Auto-refresh power button state
            setInterval(() => {
                if (currentDevice) {
                    updatePowerButton();
                }
            }, 3000);

            // Initial device scan
            scanDevices();
        </script>
    </body>
    </html>
    """


# API Routes
@app.get("/api/devices")
async def get_devices():
    """Get list of available VISA devices"""
    global rm
    if not rm:
        raise HTTPException(status_code=500, detail="VISA not initialized")

    try:
        resources = rm.list_resources()
        return list(resources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list devices: {str(e)}")


@app.post("/api/connect")
async def connect_device(request: dict):
    """Connect to a specific device"""
    global rm, instrument, device_status

    device_address = request.get("device_address")
    if not device_address:
        raise HTTPException(status_code=400, detail="Device address required")

    try:
        if instrument:
            instrument.close()

        instrument = rm.open_resource(device_address)
        idn = instrument.query("*IDN?").strip()

        device_status.update({
            "connected": True,
            "device_info": idn.split(',')[0] if ',' in idn else idn,
            "current_channel": 1
        })

        # Check initial output state
        check_initial_output_state()
        update_status()

        # Start monitoring
        start_monitoring()

        return {"success": True, "device_info": device_status["device_info"]}

    except Exception as e:
        device_status["connected"] = False
        update_status()
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


@app.post("/api/set-channel")
async def set_current_channel(request: dict):
    """Set the current active channel"""
    global device_status

    channel = request.get("channel")
    if not channel or channel not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Valid channel (1-3) required")

    device_status["current_channel"] = channel
    update_status()

    return {"success": True, "current_channel": channel}


@app.post("/api/settings")
async def apply_settings(settings: PowerSupplySettings):
    """Apply power supply settings"""
    global instrument, device_status

    if not instrument:
        raise HTTPException(status_code=400, detail="No device connected")

    # Validate voltage set vs limit
    if settings.voltage_set > settings.voltage_limit:
        raise HTTPException(status_code=400, detail="Set voltage cannot exceed voltage limit")

    try:
        # Send SCPI commands
        instrument.write(f"INST:NSEL {settings.channel}")
        instrument.write(f"SOUR:VOLT:LIM {settings.voltage_limit}")
        instrument.write("SOUR:VOLT:LIM:STAT ON")
        instrument.write(f"SOUR:VOLT {settings.voltage_set}")
        instrument.write(f"SOUR:CURR {settings.current}")

        # Update status
        device_status["last_settings"] = settings.dict()
        update_status()

        return {"success": True, "message": f"Settings applied to channel {settings.channel}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply settings: {str(e)}")


@app.post("/api/output")
async def control_output(control: OutputControl):
    """Control output state for ALL channels"""
    global instrument, device_status

    if not instrument:
        raise HTTPException(status_code=400, detail="No device connected")

    try:
        # Set output for ALL channels
        for channel in [1, 2, 3]:
            instrument.write(f"INST:NSEL {channel}")
            instrument.write(f"OUTP {'ON' if control.state else 'OFF'}")

        # Update status
        device_status["output_state"] = control.state
        update_status()

        state_text = "ON" if control.state else "OFF"
        return {"success": True, "message": f"All channels output {state_text}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to control output: {str(e)}")


@app.get("/api/status")
async def get_status():
    """Get current device status"""
    global device_status
    update_status()
    return device_status


@app.get("/api/plot-data")
async def get_plot_data():
    """Get voltage data for plotting"""
    global voltage_data, time_data, device_status

    current_channel = device_status["current_channel"]

    # Convert deque to lists and format timestamps
    times = [t.isoformat() for t in time_data[current_channel]]
    voltages = list(voltage_data[current_channel])

    return {
        "time": times,
        "voltage": voltages,
        "channel": current_channel
    }


@app.post("/api/clear-data")
async def clear_plot_data():
    """Clear all stored voltage data"""
    global voltage_data, time_data

    for ch in [1, 2, 3]:
        voltage_data[ch].clear()
        time_data[ch].clear()

    return {"success": True, "message": "Plot data cleared"}


@app.post("/api/disconnect")
async def disconnect_device():
    """Disconnect from current device"""
    global instrument, device_status

    try:
        # Stop monitoring
        stop_monitoring()

        if instrument:
            # Turn off all outputs before disconnecting
            for ch in [1, 2, 3]:
                instrument.write(f"INST:NSEL {ch}")
                instrument.write("OUTP OFF")
            instrument.close()
            instrument = None

        device_status.update({
            "connected": False,
            "device_info": None,
            "output_state": False,
            "current_channel": 1
        })
        update_status()

        return {"success": True, "message": "Disconnected successfully"}

    except Exception as e:
        return {"success": True, "message": "Disconnected (with errors)"}


if __name__ == "__main__":
    print("🚀 Starting Keithley 2230G Remote Control Server...")
    print("📱 Access the web interface at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",  # Allow external connections
        port=8000,
        reload=False
    )

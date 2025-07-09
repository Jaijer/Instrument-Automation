"""
Utility functions for the Power Supply GUI
Contains validation, formatting, and helper functions
"""

def validate_channel(channel_str):
    """Validate channel input"""
    try:
        channel = int(channel_str)
        if not (1 <= channel <= 3):
            raise ValueError("Channel must be 1, 2, or 3")
        return channel
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("Channel must be a number")
        raise e

def validate_voltage(voltage_str, max_voltage=30.0):
    """Validate voltage input"""
    try:
        voltage = float(voltage_str)
        if voltage < 0:
            raise ValueError("Voltage cannot be negative")
        if voltage > max_voltage:
            raise ValueError(f"Voltage cannot exceed {max_voltage}V")
        return voltage
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError("Voltage must be a number")
        raise e

def validate_current(current_str, max_current=5.0):
    """Validate current input"""
    try:
        current = float(current_str)
        if current < 0:
            raise ValueError("Current cannot be negative")
        if current > max_current:
            raise ValueError(f"Current cannot exceed {max_current}A")
        return current
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError("Current must be a number")
        raise e

def format_device_info(idn_string):
    """Format device identification string for display"""
    if not idn_string:
        return "No device information"

    # Split by commas and clean up
    parts = [part.strip() for part in idn_string.split(',')]
    if len(parts) >= 2:
        return f"{parts[0]} - {parts[1]}"
    return idn_string.strip()

def get_visa_resources(resource_manager):
    """Get available VISA resources with error handling"""
    try:
        resources = resource_manager.list_resources()
        return list(resources) if resources else []
    except Exception as e:
        print(f"Error listing VISA resources: {e}")
        return []

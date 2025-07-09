"""
Styling module for the Power Supply GUI
Contains all UI styling and theme definitions
"""

def get_main_stylesheet():
    """Returns the main application stylesheet with conservative colors"""
    return """
    /* Main application styling */
    QWidget {
        background-color: #ffffff;
        font-family: 'Segoe UI', 'Tahoma', Arial, sans-serif;
        font-size: 9pt;
        color: #333333;
    }
    
    /* Group boxes for sections */
    QGroupBox {
        font-weight: 600;
        font-size: 10pt;
        color: #2c3e50;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
        background-color: #fafafa;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 6px 0 6px;
        background-color: #fafafa;
        color: #2c3e50;
    }
    
    /* Labels */
    QLabel {
        color: #444444;
        font-weight: normal;
        padding: 2px;
        background-color: transparent;
    }
    
    /* Input fields */
    QLineEdit {
        border: 1px solid #cccccc;
        border-radius: 3px;
        padding: 6px 8px;
        font-size: 9pt;
        background-color: #ffffff;
        color: #333333;
        selection-background-color: #e3f2fd;
    }
    
    QLineEdit:focus {
        border-color: #666666;
        outline: none;
    }
    
    /* Combo boxes */
    QComboBox {
        border: 1px solid #cccccc;
        border-radius: 3px;
        padding: 6px 8px;
        background-color: #ffffff;
        color: #333333;
        min-width: 150px;
    }
    
    QComboBox:focus {
        border-color: #666666;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
        background-color: #f5f5f5;
    }
    
    QComboBox::down-arrow {
        width: 10px;
        height: 10px;
        background-color: #666666;
    }
    
    QComboBox QAbstractItemView {
        border: 1px solid #cccccc;
        background-color: #ffffff;
        color: #333333;
        selection-background-color: #e8e8e8;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #f8f9fa;
        color: #333333;
        border: 1px solid #cccccc;
        border-radius: 3px;
        padding: 8px 16px;
        font-weight: 500;
        font-size: 9pt;
        min-height: 16px;
    }
    
    QPushButton:hover {
        background-color: #e9ecef;
        border-color: #999999;
    }
    
    QPushButton:pressed {
        background-color: #dee2e6;
    }
    
    QPushButton:disabled {
        background-color: #f8f9fa;
        color: #999999;
        border-color: #e0e0e0;
    }
    """

def get_button_styles():
    """Returns specific button styling"""
    return {
        'connect': """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: 1px solid #28a745;
            }
            QPushButton:hover {
                background-color: #218838;
                border-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                border-color: #6c757d;
                color: white;
            }
        """,

        'refresh': """
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: 1px solid #17a2b8;
            }
            QPushButton:hover {
                background-color: #138496;
                border-color: #117a8b;
            }
        """,

        'output_off': """
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: 1px solid #dc3545;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #c82333;
                border-color: #bd2130;
            }
        """,

        'output_on': """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: 1px solid #28a745;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #218838;
                border-color: #1e7e34;
            }
        """,

        'apply': """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: 1px solid #007bff;
            }
            QPushButton:hover {
                background-color: #0069d9;
                border-color: #0062cc;
            }
        """
    }

def get_status_styles():
    """Returns status label styling"""
    return {
        'default': """
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 6px 10px;
                color: #495057;
            }
        """,

        'connected': """
            QLabel {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 3px;
                padding: 6px 10px;
                color: #155724;
            }
        """,

        'disconnected': """
            QLabel {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 3px;
                padding: 6px 10px;
                color: #721c24;
            }
        """,

        'warning': """
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 3px;
                padding: 6px 10px;
                color: #856404;
            }
        """
    }

"""
Configuration file for Hospital Management System
Contains all constants and paths used throughout the application
"""

import os

# Database paths
DATABASE_PATH = "data/"
PATIENTS_FILE = "data/patients.json"
STAFF_FILE = "data/staff.json"
APPOINTMENTS_FILE = "data/appointments.json"
BILLING_FILE = "data/billing.json"

# Log file path
LOG_PATH = "logs/"
LOG_FILE = "logs/hospital.log"

# Application constants
APP_NAME = "Hospital Management System"
APP_VERSION = "1.0.0"

def ensure_directories():
    """
    Ensure that required directories exist, create them if they don't
    """
    directories = [DATABASE_PATH, LOG_PATH]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def initialize_data_files():
    """
    Initialize JSON data files with empty structures if they don't exist
    """
    files_to_initialize = {
        PATIENTS_FILE: [],
        STAFF_FILE: [],
        APPOINTMENTS_FILE: [],
        BILLING_FILE: []
    }
    
    for file_path, initial_data in files_to_initialize.items():
        if not os.path.exists(file_path):
            import json
            with open(file_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
            print(f"Initialized data file: {file_path}")

if __name__ == "__main__":
    ensure_directories()
    initialize_data_files()

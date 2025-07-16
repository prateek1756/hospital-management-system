"""
Database operations for Hospital Management System
Handles JSON file read/write operations with error handling
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import config
from utils import log_error

def load_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load data from JSON file
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        List[Dict[str, Any]]: Loaded data or empty list if file doesn't exist
    """
    try:
        if not os.path.exists(file_path):
            # Initialize empty file if it doesn't exist
            save_data(file_path, [])
            return []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
            
    except json.JSONDecodeError as e:
        error_msg = f"JSON decode error in {file_path}: {str(e)}"
        log_error(error_msg)
        print(f"Error: Invalid JSON format in {file_path}")
        return []
        
    except FileNotFoundError as e:
        error_msg = f"File not found: {file_path} - {str(e)}"
        log_error(error_msg)
        # Create the file with empty data
        save_data(file_path, [])
        return []
        
    except PermissionError as e:
        error_msg = f"Permission denied accessing {file_path}: {str(e)}"
        log_error(error_msg)
        print(f"Error: Permission denied accessing {file_path}")
        return []
        
    except Exception as e:
        error_msg = f"Unexpected error loading {file_path}: {str(e)}"
        log_error(error_msg)
        print(f"Error: Failed to load data from {file_path}")
        return []

def save_data(file_path: str, data: List[Dict[str, Any]]) -> bool:
    """
    Save data to JSON file
    
    Args:
        file_path (str): Path to the JSON file
        data (List[Dict[str, Any]]): Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create backup of existing file
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup"
            try:
                with open(file_path, 'r', encoding='utf-8') as original:
                    with open(backup_path, 'w', encoding='utf-8') as backup:
                        backup.write(original.read())
            except Exception as backup_error:
                log_error(f"Failed to create backup for {file_path}: {str(backup_error)}")
        
        # Save the data
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
        return True
        
    except PermissionError as e:
        error_msg = f"Permission denied writing to {file_path}: {str(e)}"
        log_error(error_msg)
        print(f"Error: Permission denied writing to {file_path}")
        return False
        
    except OSError as e:
        error_msg = f"OS error writing to {file_path}: {str(e)}"
        log_error(error_msg)
        print(f"Error: Failed to write to {file_path}")
        return False
        
    except Exception as e:
        error_msg = f"Unexpected error saving to {file_path}: {str(e)}"
        log_error(error_msg)
        print(f"Error: Failed to save data to {file_path}")
        return False

def find_by_id(data: List[Dict[str, Any]], record_id: str) -> Optional[Dict[str, Any]]:
    """
    Find a record by ID in the data list
    
    Args:
        data (List[Dict[str, Any]]): List of records
        record_id (str): ID to search for
        
    Returns:
        Optional[Dict[str, Any]]: Found record or None
    """
    try:
        for record in data:
            if record.get('id') == record_id:
                return record
        return None
    except Exception as e:
        log_error(f"Error finding record by ID {record_id}: {str(e)}")
        return None

def update_record(data: List[Dict[str, Any]], record_id: str, 
                 updated_fields: Dict[str, Any]) -> bool:
    """
    Update a record in the data list
    
    Args:
        data (List[Dict[str, Any]]): List of records
        record_id (str): ID of record to update
        updated_fields (Dict[str, Any]): Fields to update
        
    Returns:
        bool: True if record was found and updated, False otherwise
    """
    try:
        for i, record in enumerate(data):
            if record.get('id') == record_id:
                # Update the record
                data[i].update(updated_fields)
                data[i]['updated_at'] = datetime.now().isoformat()
                return True
        return False
    except Exception as e:
        log_error(f"Error updating record {record_id}: {str(e)}")
        return False

def delete_record(data: List[Dict[str, Any]], record_id: str) -> bool:
    """
    Delete a record from the data list
    
    Args:
        data (List[Dict[str, Any]]): List of records
        record_id (str): ID of record to delete
        
    Returns:
        bool: True if record was found and deleted, False otherwise
    """
    try:
        for i, record in enumerate(data):
            if record.get('id') == record_id:
                del data[i]
                return True
        return False
    except Exception as e:
        log_error(f"Error deleting record {record_id}: {str(e)}")
        return False

def get_next_id(data: List[Dict[str, Any]], prefix: str = "") -> str:
    """
    Generate next sequential ID for records
    
    Args:
        data (List[Dict[str, Any]]): Existing records
        prefix (str): Prefix for the ID
        
    Returns:
        str: Next available ID
    """
    try:
        if not data:
            return f"{prefix}001" if prefix else "001"
        
        # Extract numeric parts from existing IDs
        max_num = 0
        for record in data:
            record_id = record.get('id', '')
            if prefix and record_id.startswith(prefix):
                num_part = record_id[len(prefix):]
            else:
                num_part = record_id
            
            try:
                num = int(num_part)
                max_num = max(max_num, num)
            except ValueError:
                continue
        
        next_num = max_num + 1
        return f"{prefix}{next_num:03d}"
        
    except Exception as e:
        log_error(f"Error generating next ID: {str(e)}")
        import uuid
        return str(uuid.uuid4())

def validate_data_integrity(file_path: str) -> bool:
    """
    Validate the integrity of data in a JSON file
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    try:
        data = load_data(file_path)
        
        # Check if data is a list
        if not isinstance(data, list):
            return False
        
        # Check if all records have required 'id' field
        for record in data:
            if not isinstance(record, dict) or 'id' not in record:
                return False
        
        return True
        
    except Exception as e:
        log_error(f"Error validating data integrity for {file_path}: {str(e)}")
        return False

# Initialize database files on import
if __name__ == "__main__":
    config.ensure_directories()
    config.initialize_data_files()

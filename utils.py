"""
Utility functions for Hospital Management System
Contains logging, validation, and UI helper functions
"""

import os
import logging
from datetime import datetime
from typing import Any, Union, List
import config

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    try:
        # Ensure log directory exists
        if not os.path.exists(config.LOG_PATH):
            os.makedirs(config.LOG_PATH)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    except Exception as e:
        print(f"Error setting up logging: {str(e)}")
        return None

# Initialize logger
logger = setup_logging()

def log_error(error_message: str):
    """
    Log error message to file and console
    
    Args:
        error_message (str): Error message to log
    """
    try:
        if logger:
            logger.error(error_message)
        else:
            # Fallback logging if logger setup failed
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - ERROR - {error_message}\n"
            
            try:
                with open(config.LOG_FILE, 'a', encoding='utf-8') as log_file:
                    log_file.write(log_entry)
            except Exception:
                pass  # Silent fail for logging errors
            
            print(f"ERROR: {error_message}")
    except Exception:
        pass  # Silent fail for logging errors

def log_info(info_message: str):
    """
    Log info message to file
    
    Args:
        info_message (str): Info message to log
    """
    try:
        if logger:
            logger.info(info_message)
    except Exception:
        pass  # Silent fail for logging errors

def validate_input(value: Any, expected_type: type, field_name: str = "") -> bool:
    """
    Validate input value against expected type
    
    Args:
        value: Value to validate
        expected_type: Expected type
        field_name: Name of the field being validated
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if expected_type == str:
            return isinstance(value, str) and len(value.strip()) > 0
        elif expected_type == int:
            if isinstance(value, str):
                try:
                    int(value)
                    return True
                except ValueError:
                    return False
            return isinstance(value, int)
        elif expected_type == float:
            if isinstance(value, str):
                try:
                    float(value)
                    return True
                except ValueError:
                    return False
            return isinstance(value, (int, float))
        else:
            return isinstance(value, expected_type)
    except Exception as e:
        log_error(f"Error validating input for {field_name}: {str(e)}")
        return False

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Remove common separators
        cleaned_phone = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '')
        
        # Check if it contains only digits and has reasonable length
        return cleaned_phone.isdigit() and 10 <= len(cleaned_phone) <= 15
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email (str): Email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        return '@' in email and '.' in email.split('@')[1] and len(email) > 5
    except Exception:
        return False

def validate_date(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD)
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_time(time_str: str) -> bool:
    """
    Validate time format (HH:MM)
    
    Args:
        time_str (str): Time string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def clear_screen():
    """Clear terminal screen for clean UI transitions"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        # If clear doesn't work, print newlines
        print('\n' * 50)

def print_header(title: str):
    """
    Print a formatted header for sections
    
    Args:
        title (str): Title to display
    """
    print("\n" + "=" * 60)
    print(f"{title:^60}")
    print("=" * 60)

def print_separator():
    """Print a separator line"""
    print("-" * 60)

def format_table_row(columns: List[str], widths: List[int]) -> str:
    """
    Format a table row with specified column widths
    
    Args:
        columns (List[str]): Column values
        widths (List[int]): Column widths
        
    Returns:
        str: Formatted row
    """
    try:
        formatted_columns = []
        for i, (col, width) in enumerate(zip(columns, widths)):
            col_str = str(col)[:width-1]  # Truncate if too long
            formatted_columns.append(col_str.ljust(width))
        return "| " + " | ".join(formatted_columns) + " |"
    except Exception as e:
        log_error(f"Error formatting table row: {str(e)}")
        return "| " + " | ".join(str(col) for col in columns) + " |"

def print_table(headers: List[str], rows: List[List[str]], widths: List[int] = None):
    """
    Print a formatted table
    
    Args:
        headers (List[str]): Table headers
        rows (List[List[str]]): Table rows
        widths (List[int], optional): Column widths
    """
    try:
        if not widths:
            # Calculate default widths
            widths = []
            for i, header in enumerate(headers):
                max_width = len(header)
                for row in rows:
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])))
                widths.append(min(max_width + 2, 20))  # Cap at 20 characters
        
        # Print header
        print(format_table_row(headers, widths))
        print("+" + "+".join("-" * width for width in widths) + "+")
        
        # Print rows
        for row in rows:
            print(format_table_row(row, widths))
            
    except Exception as e:
        log_error(f"Error printing table: {str(e)}")
        # Fallback simple print
        print(" | ".join(headers))
        print("-" * 40)
        for row in rows:
            print(" | ".join(str(col) for col in row))

def get_user_input(prompt: str, input_type: type = str, required: bool = True) -> Any:
    """
    Get validated user input
    
    Args:
        prompt (str): Input prompt
        input_type (type): Expected input type
        required (bool): Whether input is required
        
    Returns:
        Any: Validated user input
    """
    while True:
        try:
            user_input = input(f"{prompt}: ").strip()
            
            if not user_input and not required:
                return None
            
            if not user_input and required:
                print("This field is required. Please enter a value.")
                continue
            
            if input_type == str:
                return user_input
            elif input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            else:
                return user_input
                
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None
        except Exception as e:
            log_error(f"Error getting user input: {str(e)}")
            print("An error occurred. Please try again.")

def confirm_action(message: str) -> bool:
    """
    Get user confirmation for an action
    
    Args:
        message (str): Confirmation message
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    try:
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return False
    except Exception as e:
        log_error(f"Error getting confirmation: {str(e)}")
        return False

def pause():
    """Pause execution until user presses Enter"""
    try:
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        pass
    except Exception:
        pass

# Initialize logging on import
if __name__ == "__main__":
    log_info("Utils module initialized")

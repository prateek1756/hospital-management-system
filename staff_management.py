"""
Staff Management Module for Hospital Management System
Handles CRUD operations for hospital staff records
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import config
import database
from models import Staff
from utils import log_error, log_info, validate_input, validate_phone, print_table, get_user_input, confirm_action

def add_staff(staff_data: Dict[str, Any] = None) -> bool:
    """
    Add a new staff member to the system
    
    Args:
        staff_data (Dict[str, Any], optional): Staff data dictionary
        
    Returns:
        bool: True if staff added successfully, False otherwise
    """
    try:
        if not staff_data:
            # Interactive input
            print("\n--- Add New Staff Member ---")
            name = get_user_input("Staff Name", str, True)
            if not name:
                return False
            
            print("Available roles: Doctor, Nurse, Admin, Technician, Pharmacist")
            role = get_user_input("Role", str, True)
            if not role:
                return False
            
            contact = get_user_input("Contact Number", str, True)
            if not validate_phone(contact):
                print("Invalid phone number format.")
                return False
            
            specialization = get_user_input("Specialization (optional)", str, False) or ""
            
            staff_data = {
                'name': name,
                'role': role.title(),
                'contact': contact,
                'specialization': specialization
            }
        
        # Validate required fields
        required_fields = ['name', 'role', 'contact']
        for field in required_fields:
            if field not in staff_data or not staff_data[field]:
                log_error(f"Missing required field: {field}")
                print(f"Error: Missing required field: {field}")
                return False
        
        # Create staff object
        staff = Staff(
            name=staff_data['name'],
            role=staff_data['role'],
            contact=staff_data['contact'],
            specialization=staff_data.get('specialization', '')
        )
        
        # Load existing staff
        staff_list = database.load_data(config.STAFF_FILE)
        
        # Add new staff member
        staff_list.append(staff.to_dict())
        
        # Save to file
        if database.save_data(config.STAFF_FILE, staff_list):
            log_info(f"Staff member added successfully: {staff.name} (ID: {staff.id})")
            print(f"Staff member added successfully! Staff ID: {staff.id}")
            return True
        else:
            print("Error: Failed to save staff data.")
            return False
            
    except Exception as e:
        error_msg = f"Error adding staff member: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def update_staff(staff_id: str, updated_data: Dict[str, Any] = None) -> bool:
    """
    Update an existing staff record
    
    Args:
        staff_id (str): ID of the staff member to update
        updated_data (Dict[str, Any], optional): Updated staff data
        
    Returns:
        bool: True if staff updated successfully, False otherwise
    """
    try:
        # Load existing staff
        staff_list = database.load_data(config.STAFF_FILE)
        
        # Find staff member
        staff_record = database.find_by_id(staff_list, staff_id)
        if not staff_record:
            print(f"Error: Staff member with ID {staff_id} not found.")
            return False
        
        if not updated_data:
            # Interactive update
            print(f"\n--- Update Staff: {staff_record['name']} ---")
            print("Leave fields empty to keep current values:")
            
            name = get_user_input(f"Name (current: {staff_record['name']})", str, False)
            role = get_user_input(f"Role (current: {staff_record['role']})", str, False)
            contact = get_user_input(f"Contact (current: {staff_record['contact']})", str, False)
            specialization = get_user_input(f"Specialization (current: {staff_record.get('specialization', 'None')})", str, False)
            
            updated_data = {}
            if name:
                updated_data['name'] = name
            if role:
                updated_data['role'] = role.title()
            if contact and validate_phone(contact):
                updated_data['contact'] = contact
            elif contact:
                print("Invalid phone number format. Keeping current value.")
            if specialization is not None:
                updated_data['specialization'] = specialization
        
        if not updated_data:
            print("No changes made.")
            return True
        
        # Update the record
        if database.update_record(staff_list, staff_id, updated_data):
            if database.save_data(config.STAFF_FILE, staff_list):
                log_info(f"Staff member updated successfully: ID {staff_id}")
                print("Staff member updated successfully!")
                return True
            else:
                print("Error: Failed to save updated staff data.")
                return False
        else:
            print("Error: Failed to update staff record.")
            return False
            
    except Exception as e:
        error_msg = f"Error updating staff member {staff_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def delete_staff(staff_id: str) -> bool:
    """
    Delete a staff record
    
    Args:
        staff_id (str): ID of the staff member to delete
        
    Returns:
        bool: True if staff deleted successfully, False otherwise
    """
    try:
        # Load existing staff
        staff_list = database.load_data(config.STAFF_FILE)
        
        # Find staff member
        staff_record = database.find_by_id(staff_list, staff_id)
        if not staff_record:
            print(f"Error: Staff member with ID {staff_id} not found.")
            return False
        
        # Confirm deletion
        if not confirm_action(f"Are you sure you want to delete staff member '{staff_record['name']}'?"):
            print("Deletion cancelled.")
            return False
        
        # Delete the record
        if database.delete_record(staff_list, staff_id):
            if database.save_data(config.STAFF_FILE, staff_list):
                log_info(f"Staff member deleted successfully: {staff_record['name']} (ID: {staff_id})")
                print("Staff member deleted successfully!")
                return True
            else:
                print("Error: Failed to save changes after deletion.")
                return False
        else:
            print("Error: Failed to delete staff record.")
            return False
            
    except Exception as e:
        error_msg = f"Error deleting staff member {staff_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def get_staff(staff_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific staff record
    
    Args:
        staff_id (str): ID of the staff member to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Staff record or None if not found
    """
    try:
        staff_list = database.load_data(config.STAFF_FILE)
        staff_record = database.find_by_id(staff_list, staff_id)
        
        if staff_record:
            return staff_record
        else:
            print(f"Staff member with ID {staff_id} not found.")
            return None
            
    except Exception as e:
        error_msg = f"Error retrieving staff member {staff_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return None

def list_staff() -> List[Dict[str, Any]]:
    """
    List all staff records
    
    Returns:
        List[Dict[str, Any]]: List of all staff records
    """
    try:
        staff_list = database.load_data(config.STAFF_FILE)
        
        if not staff_list:
            print("No staff members found in the system.")
            return []
        
        # Display staff in a table format
        headers = ["ID", "Name", "Role", "Contact", "Specialization"]
        rows = []
        
        for staff in staff_list:
            specialization = staff.get('specialization', 'None')
            if len(specialization) > 20:
                specialization = specialization[:17] + "..."
            
            rows.append([
                staff['id'][:8] + "...",  # Truncate ID for display
                staff['name'],
                staff['role'],
                staff['contact'],
                specialization
            ])
        
        print(f"\n--- Staff List ({len(staff_list)} members) ---")
        print_table(headers, rows)
        
        return staff_list
        
    except Exception as e:
        error_msg = f"Error listing staff: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def search_staff(search_term: str) -> List[Dict[str, Any]]:
    """
    Search for staff by name, role, or contact
    
    Args:
        search_term (str): Term to search for
        
    Returns:
        List[Dict[str, Any]]: List of matching staff records
    """
    try:
        staff_list = database.load_data(config.STAFF_FILE)
        
        if not staff_list:
            print("No staff members found in the system.")
            return []
        
        # Search in name, role, and contact fields
        matching_staff = []
        search_term_lower = search_term.lower()
        
        for staff in staff_list:
            if (search_term_lower in staff['name'].lower() or 
                search_term_lower in staff['role'].lower() or
                search_term_lower in staff['contact']):
                matching_staff.append(staff)
        
        if matching_staff:
            headers = ["ID", "Name", "Role", "Contact", "Specialization"]
            rows = []
            
            for staff in matching_staff:
                specialization = staff.get('specialization', 'None')
                if len(specialization) > 20:
                    specialization = specialization[:17] + "..."
                
                rows.append([
                    staff['id'][:8] + "...",
                    staff['name'],
                    staff['role'],
                    staff['contact'],
                    specialization
                ])
            
            print(f"\n--- Search Results ({len(matching_staff)} found) ---")
            print_table(headers, rows)
        else:
            print(f"No staff members found matching '{search_term}'.")
        
        return matching_staff
        
    except Exception as e:
        error_msg = f"Error searching staff: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def list_doctors() -> List[Dict[str, Any]]:
    """
    List all doctors for appointment scheduling
    
    Returns:
        List[Dict[str, Any]]: List of doctor records
    """
    try:
        staff_list = database.load_data(config.STAFF_FILE)
        doctors = [staff for staff in staff_list if staff['role'].lower() == 'doctor']
        
        if not doctors:
            print("No doctors found in the system.")
            return []
        
        headers = ["ID", "Name", "Specialization", "Contact"]
        rows = []
        
        for doctor in doctors:
            specialization = doctor.get('specialization', 'General')
            rows.append([
                doctor['id'][:8] + "...",
                doctor['name'],
                specialization,
                doctor['contact']
            ])
        
        print(f"\n--- Available Doctors ({len(doctors)} doctors) ---")
        print_table(headers, rows)
        
        return doctors
        
    except Exception as e:
        error_msg = f"Error listing doctors: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def staff_management_menu():
    """Display staff management menu and handle user choices"""
    while True:
        try:
            print("\n" + "=" * 50)
            print("           STAFF MANAGEMENT")
            print("=" * 50)
            print("1. Add New Staff Member")
            print("2. View All Staff")
            print("3. Search Staff")
            print("4. Update Staff")
            print("5. Delete Staff")
            print("6. View Doctors Only")
            print("7. Back to Main Menu")
            print("-" * 50)
            
            choice = get_user_input("Enter your choice (1-7)", str, True)
            
            if choice == '1':
                add_staff()
            elif choice == '2':
                list_staff()
            elif choice == '3':
                search_term = get_user_input("Enter name, role, or contact to search", str, True)
                if search_term:
                    search_staff(search_term)
            elif choice == '4':
                staff_id = get_user_input("Enter Staff ID to update", str, True)
                if staff_id:
                    update_staff(staff_id)
            elif choice == '5':
                staff_id = get_user_input("Enter Staff ID to delete", str, True)
                if staff_id:
                    delete_staff(staff_id)
            elif choice == '6':
                list_doctors()
            elif choice == '7':
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
                
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            break
        except Exception as e:
            log_error(f"Error in staff management menu: {str(e)}")
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    staff_management_menu()

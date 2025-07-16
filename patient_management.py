"""
Patient Management Module for Hospital Management System
Handles CRUD operations for patient records
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import config
import database
from models import Patient
from utils import log_error, log_info, validate_input, validate_phone, print_table, get_user_input, confirm_action

def add_patient(patient_data: Dict[str, Any] = None) -> bool:
    """
    Add a new patient to the system
    
    Args:
        patient_data (Dict[str, Any], optional): Patient data dictionary
        
    Returns:
        bool: True if patient added successfully, False otherwise
    """
    try:
        if not patient_data:
            # Interactive input
            print("\n--- Add New Patient ---")
            name = get_user_input("Patient Name", str, True)
            if not name:
                return False
            
            age = get_user_input("Age", int, True)
            if age is None or age < 0 or age > 150:
                print("Invalid age. Please enter a valid age between 0 and 150.")
                return False
            
            gender = get_user_input("Gender (M/F/Other)", str, True)
            if gender.upper() not in ['M', 'F', 'MALE', 'FEMALE', 'OTHER']:
                print("Invalid gender. Please enter M, F, or Other.")
                return False
            
            contact = get_user_input("Contact Number", str, True)
            if not validate_phone(contact):
                print("Invalid phone number format.")
                return False
            
            medical_history = get_user_input("Medical History", str, False) or ""
            
            patient_data = {
                'name': name,
                'age': age,
                'gender': gender.capitalize(),
                'contact': contact,
                'medical_history': medical_history
            }
        
        # Validate required fields
        required_fields = ['name', 'age', 'gender', 'contact']
        for field in required_fields:
            if field not in patient_data or not patient_data[field]:
                log_error(f"Missing required field: {field}")
                print(f"Error: Missing required field: {field}")
                return False
        
        # Create patient object
        patient = Patient(
            name=patient_data['name'],
            age=int(patient_data['age']),
            gender=patient_data['gender'],
            contact=patient_data['contact'],
            medical_history=patient_data.get('medical_history', '')
        )
        
        # Load existing patients
        patients_data = database.load_data(config.PATIENTS_FILE)
        
        # Add new patient
        patients_data.append(patient.to_dict())
        
        # Save to file
        if database.save_data(config.PATIENTS_FILE, patients_data):
            log_info(f"Patient added successfully: {patient.name} (ID: {patient.id})")
            print(f"Patient added successfully! Patient ID: {patient.id}")
            return True
        else:
            print("Error: Failed to save patient data.")
            return False
            
    except Exception as e:
        error_msg = f"Error adding patient: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def update_patient(patient_id: str, updated_data: Dict[str, Any] = None) -> bool:
    """
    Update an existing patient record
    
    Args:
        patient_id (str): ID of the patient to update
        updated_data (Dict[str, Any], optional): Updated patient data
        
    Returns:
        bool: True if patient updated successfully, False otherwise
    """
    try:
        # Load existing patients
        patients_data = database.load_data(config.PATIENTS_FILE)
        
        # Find patient
        patient_record = database.find_by_id(patients_data, patient_id)
        if not patient_record:
            print(f"Error: Patient with ID {patient_id} not found.")
            return False
        
        if not updated_data:
            # Interactive update
            print(f"\n--- Update Patient: {patient_record['name']} ---")
            print("Leave fields empty to keep current values:")
            
            name = get_user_input(f"Name (current: {patient_record['name']})", str, False)
            age_input = get_user_input(f"Age (current: {patient_record['age']})", str, False)
            gender = get_user_input(f"Gender (current: {patient_record['gender']})", str, False)
            contact = get_user_input(f"Contact (current: {patient_record['contact']})", str, False)
            medical_history = get_user_input(f"Medical History (current: {patient_record.get('medical_history', 'None')})", str, False)
            
            updated_data = {}
            if name:
                updated_data['name'] = name
            if age_input:
                try:
                    age = int(age_input)
                    if 0 <= age <= 150:
                        updated_data['age'] = age
                    else:
                        print("Invalid age. Keeping current value.")
                except ValueError:
                    print("Invalid age format. Keeping current value.")
            if gender and gender.upper() in ['M', 'F', 'MALE', 'FEMALE', 'OTHER']:
                updated_data['gender'] = gender.capitalize()
            if contact and validate_phone(contact):
                updated_data['contact'] = contact
            elif contact:
                print("Invalid phone number format. Keeping current value.")
            if medical_history is not None:
                updated_data['medical_history'] = medical_history
        
        if not updated_data:
            print("No changes made.")
            return True
        
        # Update the record
        if database.update_record(patients_data, patient_id, updated_data):
            if database.save_data(config.PATIENTS_FILE, patients_data):
                log_info(f"Patient updated successfully: ID {patient_id}")
                print("Patient updated successfully!")
                return True
            else:
                print("Error: Failed to save updated patient data.")
                return False
        else:
            print("Error: Failed to update patient record.")
            return False
            
    except Exception as e:
        error_msg = f"Error updating patient {patient_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def delete_patient(patient_id: str) -> bool:
    """
    Delete a patient record
    
    Args:
        patient_id (str): ID of the patient to delete
        
    Returns:
        bool: True if patient deleted successfully, False otherwise
    """
    try:
        # Load existing patients
        patients_data = database.load_data(config.PATIENTS_FILE)
        
        # Find patient
        patient_record = database.find_by_id(patients_data, patient_id)
        if not patient_record:
            print(f"Error: Patient with ID {patient_id} not found.")
            return False
        
        # Confirm deletion
        if not confirm_action(f"Are you sure you want to delete patient '{patient_record['name']}'?"):
            print("Deletion cancelled.")
            return False
        
        # Delete the record
        if database.delete_record(patients_data, patient_id):
            if database.save_data(config.PATIENTS_FILE, patients_data):
                log_info(f"Patient deleted successfully: {patient_record['name']} (ID: {patient_id})")
                print("Patient deleted successfully!")
                return True
            else:
                print("Error: Failed to save changes after deletion.")
                return False
        else:
            print("Error: Failed to delete patient record.")
            return False
            
    except Exception as e:
        error_msg = f"Error deleting patient {patient_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def get_patient(patient_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific patient record
    
    Args:
        patient_id (str): ID of the patient to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Patient record or None if not found
    """
    try:
        patients_data = database.load_data(config.PATIENTS_FILE)
        patient_record = database.find_by_id(patients_data, patient_id)
        
        if patient_record:
            return patient_record
        else:
            print(f"Patient with ID {patient_id} not found.")
            return None
            
    except Exception as e:
        error_msg = f"Error retrieving patient {patient_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return None

def list_patients() -> List[Dict[str, Any]]:
    """
    List all patient records
    
    Returns:
        List[Dict[str, Any]]: List of all patient records
    """
    try:
        patients_data = database.load_data(config.PATIENTS_FILE)
        
        if not patients_data:
            print("No patients found in the system.")
            return []
        
        # Display patients in a table format
        headers = ["ID", "Name", "Age", "Gender", "Contact", "Medical History"]
        rows = []
        
        for patient in patients_data:
            medical_history = patient.get('medical_history', 'None')
            if len(medical_history) > 30:
                medical_history = medical_history[:27] + "..."
            
            rows.append([
                patient['id'][:8] + "...",  # Truncate ID for display
                patient['name'],
                str(patient['age']),
                patient['gender'],
                patient['contact'],
                medical_history
            ])
        
        print(f"\n--- Patient List ({len(patients_data)} patients) ---")
        print_table(headers, rows)
        
        return patients_data
        
    except Exception as e:
        error_msg = f"Error listing patients: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def search_patients(search_term: str) -> List[Dict[str, Any]]:
    """
    Search for patients by name or contact
    
    Args:
        search_term (str): Term to search for
        
    Returns:
        List[Dict[str, Any]]: List of matching patient records
    """
    try:
        patients_data = database.load_data(config.PATIENTS_FILE)
        
        if not patients_data:
            print("No patients found in the system.")
            return []
        
        # Search in name and contact fields
        matching_patients = []
        search_term_lower = search_term.lower()
        
        for patient in patients_data:
            if (search_term_lower in patient['name'].lower() or 
                search_term_lower in patient['contact']):
                matching_patients.append(patient)
        
        if matching_patients:
            headers = ["ID", "Name", "Age", "Gender", "Contact"]
            rows = []
            
            for patient in matching_patients:
                rows.append([
                    patient['id'][:8] + "...",
                    patient['name'],
                    str(patient['age']),
                    patient['gender'],
                    patient['contact']
                ])
            
            print(f"\n--- Search Results ({len(matching_patients)} found) ---")
            print_table(headers, rows)
        else:
            print(f"No patients found matching '{search_term}'.")
        
        return matching_patients
        
    except Exception as e:
        error_msg = f"Error searching patients: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def patient_management_menu():
    """Display patient management menu and handle user choices"""
    while True:
        try:
            print("\n" + "=" * 50)
            print("           PATIENT MANAGEMENT")
            print("=" * 50)
            print("1. Add New Patient")
            print("2. View All Patients")
            print("3. Search Patient")
            print("4. Update Patient")
            print("5. Delete Patient")
            print("6. Back to Main Menu")
            print("-" * 50)
            
            choice = get_user_input("Enter your choice (1-6)", str, True)
            
            if choice == '1':
                add_patient()
            elif choice == '2':
                list_patients()
            elif choice == '3':
                search_term = get_user_input("Enter name or contact to search", str, True)
                if search_term:
                    search_patients(search_term)
            elif choice == '4':
                patient_id = get_user_input("Enter Patient ID to update", str, True)
                if patient_id:
                    update_patient(patient_id)
            elif choice == '5':
                patient_id = get_user_input("Enter Patient ID to delete", str, True)
                if patient_id:
                    delete_patient(patient_id)
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
                
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            break
        except Exception as e:
            log_error(f"Error in patient management menu: {str(e)}")
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    patient_management_menu()

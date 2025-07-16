"""
Appointment Management Module for Hospital Management System
Handles scheduling, updating, and cancellation of appointments
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import config
import database
from models import Appointment
from utils import (log_error, log_info, validate_date, validate_time, 
                  print_table, get_user_input, confirm_action)
import patient_management
import staff_management

def schedule_appointment(appointment_data: Dict[str, Any] = None) -> bool:
    """
    Schedule a new appointment
    
    Args:
        appointment_data (Dict[str, Any], optional): Appointment data dictionary
        
    Returns:
        bool: True if appointment scheduled successfully, False otherwise
    """
    try:
        if not appointment_data:
            # Interactive input
            print("\n--- Schedule New Appointment ---")
            
            # Show available patients
            patients = patient_management.list_patients()
            if not patients:
                print("No patients found. Please add patients first.")
                return False
            
            patient_id = get_user_input("Enter Patient ID", str, True)
            if not patient_id:
                return False
            
            # Verify patient exists
            patient = patient_management.get_patient(patient_id)
            if not patient:
                return False
            
            # Show available doctors
            doctors = staff_management.list_doctors()
            if not doctors:
                print("No doctors found. Please add doctors first.")
                return False
            
            doctor_id = get_user_input("Enter Doctor ID", str, True)
            if not doctor_id:
                return False
            
            # Verify doctor exists
            doctor = staff_management.get_staff(doctor_id)
            if not doctor or doctor['role'].lower() != 'doctor':
                print("Invalid doctor ID or staff member is not a doctor.")
                return False
            
            # Get appointment date
            date = get_user_input("Enter appointment date (YYYY-MM-DD)", str, True)
            if not validate_date(date):
                print("Invalid date format. Please use YYYY-MM-DD.")
                return False
            
            # Check if date is not in the past
            appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
            if appointment_date < datetime.now().date():
                print("Cannot schedule appointments in the past.")
                return False
            
            # Get appointment time
            time = get_user_input("Enter appointment time (HH:MM)", str, True)
            if not validate_time(time):
                print("Invalid time format. Please use HH:MM (24-hour format).")
                return False
            
            notes = get_user_input("Additional notes (optional)", str, False) or ""
            
            appointment_data = {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'date': date,
                'time': time,
                'status': 'scheduled',
                'notes': notes
            }
        
        # Check for scheduling conflicts
        if not check_appointment_conflict(appointment_data['doctor_id'], 
                                        appointment_data['date'], 
                                        appointment_data['time']):
            print("Scheduling conflict detected. Doctor is not available at this time.")
            return False
        
        # Create appointment object
        appointment = Appointment(
            patient_id=appointment_data['patient_id'],
            doctor_id=appointment_data['doctor_id'],
            date=appointment_data['date'],
            time=appointment_data['time'],
            status=appointment_data.get('status', 'scheduled'),
            notes=appointment_data.get('notes', '')
        )
        
        # Load existing appointments
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        
        # Add new appointment
        appointments_data.append(appointment.to_dict())
        
        # Save to file
        if database.save_data(config.APPOINTMENTS_FILE, appointments_data):
            log_info(f"Appointment scheduled successfully: {appointment.id}")
            print(f"Appointment scheduled successfully! Appointment ID: {appointment.id}")
            return True
        else:
            print("Error: Failed to save appointment data.")
            return False
            
    except Exception as e:
        error_msg = f"Error scheduling appointment: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def check_appointment_conflict(doctor_id: str, date: str, time: str, 
                             exclude_appointment_id: str = None) -> bool:
    """
    Check if there's a scheduling conflict for a doctor
    
    Args:
        doctor_id (str): ID of the doctor
        date (str): Appointment date
        time (str): Appointment time
        exclude_appointment_id (str, optional): Appointment ID to exclude from conflict check
        
    Returns:
        bool: True if no conflict, False if conflict exists
    """
    try:
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        
        for appointment in appointments_data:
            if (appointment['doctor_id'] == doctor_id and 
                appointment['date'] == date and 
                appointment['status'] != 'cancelled' and
                appointment.get('id') != exclude_appointment_id):
                
                # Check if times are too close (within 30 minutes)
                existing_time = datetime.strptime(appointment['time'], '%H:%M').time()
                new_time = datetime.strptime(time, '%H:%M').time()
                
                # Convert to datetime for comparison
                existing_datetime = datetime.combine(datetime.today(), existing_time)
                new_datetime = datetime.combine(datetime.today(), new_time)
                
                time_diff = abs((new_datetime - existing_datetime).total_seconds() / 60)
                
                if time_diff < 30:  # 30 minutes buffer
                    return False
        
        return True
        
    except Exception as e:
        log_error(f"Error checking appointment conflict: {str(e)}")
        return False

def update_appointment(appointment_id: str, updated_data: Dict[str, Any] = None) -> bool:
    """
    Update an existing appointment
    
    Args:
        appointment_id (str): ID of the appointment to update
        updated_data (Dict[str, Any], optional): Updated appointment data
        
    Returns:
        bool: True if appointment updated successfully, False otherwise
    """
    try:
        # Load existing appointments
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        
        # Find appointment
        appointment_record = database.find_by_id(appointments_data, appointment_id)
        if not appointment_record:
            print(f"Error: Appointment with ID {appointment_id} not found.")
            return False
        
        if not updated_data:
            # Interactive update
            print(f"\n--- Update Appointment: {appointment_id[:8]}... ---")
            print("Leave fields empty to keep current values:")
            print("Available statuses: scheduled, completed, cancelled")
            
            status = get_user_input(f"Status (current: {appointment_record['status']})", str, False)
            date = get_user_input(f"Date (current: {appointment_record['date']})", str, False)
            time = get_user_input(f"Time (current: {appointment_record['time']})", str, False)
            notes = get_user_input(f"Notes (current: {appointment_record.get('notes', 'None')})", str, False)
            
            updated_data = {}
            
            if status and status.lower() in ['scheduled', 'completed', 'cancelled']:
                updated_data['status'] = status.lower()
            elif status:
                print("Invalid status. Keeping current value.")
            
            if date and validate_date(date):
                # Check if new date is not in the past
                appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
                if appointment_date >= datetime.now().date():
                    updated_data['date'] = date
                else:
                    print("Cannot reschedule to a past date. Keeping current value.")
            elif date:
                print("Invalid date format. Keeping current value.")
            
            if time and validate_time(time):
                updated_data['time'] = time
            elif time:
                print("Invalid time format. Keeping current value.")
            
            if notes is not None:
                updated_data['notes'] = notes
        
        # Check for conflicts if date or time is being changed
        if ('date' in updated_data or 'time' in updated_data):
            new_date = updated_data.get('date', appointment_record['date'])
            new_time = updated_data.get('time', appointment_record['time'])
            
            if not check_appointment_conflict(appointment_record['doctor_id'], 
                                            new_date, new_time, appointment_id):
                print("Scheduling conflict detected. Cannot update to this time.")
                return False
        
        if not updated_data:
            print("No changes made.")
            return True
        
        # Update the record
        if database.update_record(appointments_data, appointment_id, updated_data):
            if database.save_data(config.APPOINTMENTS_FILE, appointments_data):
                log_info(f"Appointment updated successfully: ID {appointment_id}")
                print("Appointment updated successfully!")
                return True
            else:
                print("Error: Failed to save updated appointment data.")
                return False
        else:
            print("Error: Failed to update appointment record.")
            return False
            
    except Exception as e:
        error_msg = f"Error updating appointment {appointment_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def cancel_appointment(appointment_id: str) -> bool:
    """
    Cancel an appointment
    
    Args:
        appointment_id (str): ID of the appointment to cancel
        
    Returns:
        bool: True if appointment cancelled successfully, False otherwise
    """
    try:
        # Load existing appointments
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        
        # Find appointment
        appointment_record = database.find_by_id(appointments_data, appointment_id)
        if not appointment_record:
            print(f"Error: Appointment with ID {appointment_id} not found.")
            return False
        
        if appointment_record['status'] == 'cancelled':
            print("Appointment is already cancelled.")
            return True
        
        # Confirm cancellation
        if not confirm_action(f"Are you sure you want to cancel this appointment?"):
            print("Cancellation aborted.")
            return False
        
        # Update status to cancelled
        updated_data = {'status': 'cancelled'}
        
        if database.update_record(appointments_data, appointment_id, updated_data):
            if database.save_data(config.APPOINTMENTS_FILE, appointments_data):
                log_info(f"Appointment cancelled successfully: ID {appointment_id}")
                print("Appointment cancelled successfully!")
                return True
            else:
                print("Error: Failed to save cancellation.")
                return False
        else:
            print("Error: Failed to cancel appointment.")
            return False
            
    except Exception as e:
        error_msg = f"Error cancelling appointment {appointment_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def get_appointment(appointment_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific appointment record
    
    Args:
        appointment_id (str): ID of the appointment to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Appointment record or None if not found
    """
    try:
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        appointment_record = database.find_by_id(appointments_data, appointment_id)
        
        if appointment_record:
            return appointment_record
        else:
            print(f"Appointment with ID {appointment_id} not found.")
            return None
            
    except Exception as e:
        error_msg = f"Error retrieving appointment {appointment_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return None

def list_appointments(status_filter: str = None) -> List[Dict[str, Any]]:
    """
    List all appointments with optional status filter
    
    Args:
        status_filter (str, optional): Filter by appointment status
        
    Returns:
        List[Dict[str, Any]]: List of appointment records
    """
    try:
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        
        if not appointments_data:
            print("No appointments found in the system.")
            return []
        
        # Filter by status if specified
        if status_filter:
            appointments_data = [apt for apt in appointments_data 
                               if apt['status'].lower() == status_filter.lower()]
        
        if not appointments_data:
            status_msg = f" with status '{status_filter}'" if status_filter else ""
            print(f"No appointments found{status_msg}.")
            return []
        
        # Get patient and doctor names for display
        patients_data = database.load_data(config.PATIENTS_FILE)
        staff_data = database.load_data(config.STAFF_FILE)
        
        patient_names = {p['id']: p['name'] for p in patients_data}
        doctor_names = {s['id']: s['name'] for s in staff_data if s['role'].lower() == 'doctor'}
        
        # Display appointments in a table format
        headers = ["ID", "Patient", "Doctor", "Date", "Time", "Status", "Notes"]
        rows = []
        
        for appointment in appointments_data:
            patient_name = patient_names.get(appointment['patient_id'], 'Unknown')
            doctor_name = doctor_names.get(appointment['doctor_id'], 'Unknown')
            notes = appointment.get('notes', '')
            if len(notes) > 20:
                notes = notes[:17] + "..."
            
            rows.append([
                appointment['id'][:8] + "...",
                patient_name,
                doctor_name,
                appointment['date'],
                appointment['time'],
                appointment['status'].title(),
                notes or 'None'
            ])
        
        status_msg = f" ({status_filter.title()})" if status_filter else ""
        print(f"\n--- Appointments List{status_msg} ({len(appointments_data)} appointments) ---")
        print_table(headers, rows)
        
        return appointments_data
        
    except Exception as e:
        error_msg = f"Error listing appointments: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def get_today_appointments() -> List[Dict[str, Any]]:
    """
    Get today's appointments
    
    Returns:
        List[Dict[str, Any]]: List of today's appointments
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        
        today_appointments = [apt for apt in appointments_data 
                            if apt['date'] == today and apt['status'] != 'cancelled']
        
        if today_appointments:
            print(f"\n--- Today's Appointments ({len(today_appointments)} appointments) ---")
            list_appointments()
        else:
            print("No appointments scheduled for today.")
        
        return today_appointments
        
    except Exception as e:
        error_msg = f"Error getting today's appointments: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def appointment_management_menu():
    """Display appointment management menu and handle user choices"""
    while True:
        try:
            print("\n" + "=" * 50)
            print("        APPOINTMENT MANAGEMENT")
            print("=" * 50)
            print("1. Schedule New Appointment")
            print("2. View All Appointments")
            print("3. View Today's Appointments")
            print("4. View by Status")
            print("5. Update Appointment")
            print("6. Cancel Appointment")
            print("7. Back to Main Menu")
            print("-" * 50)
            
            choice = get_user_input("Enter your choice (1-7)", str, True)
            
            if choice == '1':
                schedule_appointment()
            elif choice == '2':
                list_appointments()
            elif choice == '3':
                get_today_appointments()
            elif choice == '4':
                print("Available statuses: scheduled, completed, cancelled")
                status = get_user_input("Enter status to filter", str, True)
                if status:
                    list_appointments(status)
            elif choice == '5':
                appointment_id = get_user_input("Enter Appointment ID to update", str, True)
                if appointment_id:
                    update_appointment(appointment_id)
            elif choice == '6':
                appointment_id = get_user_input("Enter Appointment ID to cancel", str, True)
                if appointment_id:
                    cancel_appointment(appointment_id)
            elif choice == '7':
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
                
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            break
        except Exception as e:
            log_error(f"Error in appointment management menu: {str(e)}")
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    appointment_management_menu()

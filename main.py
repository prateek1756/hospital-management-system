"""
Main Entry Point for Hospital Management System
Provides CLI interface and coordinates all modules
"""

import sys
import os
from datetime import datetime

# Import configuration and utilities
import config
from utils import (clear_screen, print_header, get_user_input, log_info, log_error, 
                  setup_logging, pause, confirm_action)

# Import management modules
import patient_management
import staff_management
import appointment_management
import billing_management
import reports

def initialize_system():
    """Initialize the hospital management system"""
    try:
        print("Initializing Hospital Management System...")
        
        # Ensure directories exist
        config.ensure_directories()
        
        # Initialize data files
        config.initialize_data_files()
        
        # Setup logging
        setup_logging()
        
        log_info("Hospital Management System initialized successfully")
        return True
        
    except Exception as e:
        error_msg = f"Error initializing system: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def display_welcome():
    """Display welcome message and system information"""
    clear_screen()
    print("=" * 70)
    print(f"{config.APP_NAME:^70}")
    print(f"Version {config.APP_VERSION:^70}")
    print("=" * 70)
    print()
    print("Welcome to the Hospital Management System!")
    print("This system helps you manage patients, staff, appointments, and billing.")
    print()
    print(f"System initialized on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

def display_main_menu():
    """Display the main menu"""
    print("\n" + "=" * 70)
    print(f"{'HOSPITAL MANAGEMENT SYSTEM - MAIN MENU':^70}")
    print("=" * 70)
    print()
    print("  1. Patient Management")
    print("     • Add, update, delete, and view patient records")
    print("     • Search patients by name or contact")
    print()
    print("  2. Staff Management")
    print("     • Manage doctors, nurses, and administrative staff")
    print("     • View staff by role and specialization")
    print()
    print("  3. Appointment Management")
    print("     • Schedule, update, and cancel appointments")
    print("     • View daily appointments and manage conflicts")
    print()
    print("  4. Billing Management")
    print("     • Generate bills and record payments")
    print("     • Track outstanding payments and revenue")
    print()
    print("  5. Reports")
    print("     • Generate daily, monthly, and custom reports")
    print("     • View financial and patient summary reports")
    print()
    print("  6. System Information")
    print("     • View system statistics and data integrity")
    print()
    print("  7. Exit")
    print("     • Safely exit the application")
    print()
    print("-" * 70)

def display_system_info():
    """Display system information and statistics"""
    try:
        clear_screen()
        print_header("SYSTEM INFORMATION")
        
        # Load data to get statistics
        import database
        patients_data = database.load_data(config.PATIENTS_FILE)
        staff_data = database.load_data(config.STAFF_FILE)
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        bills_data = database.load_data(config.BILLING_FILE)
        
        # Calculate statistics
        total_patients = len(patients_data)
        total_staff = len(staff_data)
        total_appointments = len(appointments_data)
        total_bills = len(bills_data)
        
        # Staff breakdown
        doctors = len([s for s in staff_data if s['role'].lower() == 'doctor'])
        nurses = len([s for s in staff_data if s['role'].lower() == 'nurse'])
        admin_staff = len([s for s in staff_data if s['role'].lower() == 'admin'])
        
        # Appointment status breakdown
        scheduled_appointments = len([a for a in appointments_data if a['status'] == 'scheduled'])
        completed_appointments = len([a for a in appointments_data if a['status'] == 'completed'])
        cancelled_appointments = len([a for a in appointments_data if a['status'] == 'cancelled'])
        
        # Financial statistics
        total_revenue = sum(bill['amount'] for bill in bills_data)
        paid_bills = len([b for b in bills_data if b['status'] == 'paid'])
        outstanding_bills = len([b for b in bills_data if b['status'] in ['unpaid', 'partial']])
        
        # Display information
        print(f"\n--- SYSTEM OVERVIEW ---")
        print(f"Application: {config.APP_NAME}")
        print(f"Version: {config.APP_VERSION}")
        print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n--- DATABASE STATISTICS ---")
        print(f"Total Patients: {total_patients}")
        print(f"Total Staff Members: {total_staff}")
        print(f"  - Doctors: {doctors}")
        print(f"  - Nurses: {nurses}")
        print(f"  - Admin Staff: {admin_staff}")
        print(f"  - Other Staff: {total_staff - doctors - nurses - admin_staff}")
        
        print(f"\nTotal Appointments: {total_appointments}")
        print(f"  - Scheduled: {scheduled_appointments}")
        print(f"  - Completed: {completed_appointments}")
        print(f"  - Cancelled: {cancelled_appointments}")
        
        print(f"\nTotal Bills: {total_bills}")
        print(f"  - Paid: {paid_bills}")
        print(f"  - Outstanding: {outstanding_bills}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        
        print(f"\n--- FILE LOCATIONS ---")
        print(f"Data Directory: {config.DATABASE_PATH}")
        print(f"Log Directory: {config.LOG_PATH}")
        print(f"Patients File: {config.PATIENTS_FILE}")
        print(f"Staff File: {config.STAFF_FILE}")
        print(f"Appointments File: {config.APPOINTMENTS_FILE}")
        print(f"Billing File: {config.BILLING_FILE}")
        
        # Check data integrity
        print(f"\n--- DATA INTEGRITY CHECK ---")
        integrity_status = "OK"
        
        try:
            # Basic integrity checks
            for file_path in [config.PATIENTS_FILE, config.STAFF_FILE, 
                            config.APPOINTMENTS_FILE, config.BILLING_FILE]:
                if not database.validate_data_integrity(file_path):
                    integrity_status = "WARNING"
                    break
        except Exception as e:
            integrity_status = "ERROR"
            log_error(f"Data integrity check failed: {str(e)}")
        
        print(f"Data Integrity Status: {integrity_status}")
        
        if integrity_status != "OK":
            print("⚠️  Some data files may have integrity issues. Check logs for details.")
        else:
            print("✅ All data files are healthy.")
        
    except Exception as e:
        error_msg = f"Error displaying system information: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")

def handle_menu_choice(choice: str) -> bool:
    """
    Handle user menu choice
    
    Args:
        choice (str): User's menu choice
        
    Returns:
        bool: True to continue, False to exit
    """
    try:
        if choice == '1':
            clear_screen()
            patient_management.patient_management_menu()
        elif choice == '2':
            clear_screen()
            staff_management.staff_management_menu()
        elif choice == '3':
            clear_screen()
            appointment_management.appointment_management_menu()
        elif choice == '4':
            clear_screen()
            billing_management.billing_management_menu()
        elif choice == '5':
            clear_screen()
            reports.reports_menu()
        elif choice == '6':
            display_system_info()
            pause()
        elif choice == '7':
            if confirm_action("Are you sure you want to exit the Hospital Management System?"):
                print("\nThank you for using the Hospital Management System!")
                print("Goodbye!")
                log_info("Hospital Management System session ended")
                return False
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")
            pause()
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
        if confirm_action("Do you want to return to the main menu?"):
            return True
        else:
            print("Exiting Hospital Management System...")
            return False
    except Exception as e:
        error_msg = f"Error handling menu choice: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        pause()
        return True

def main():
    """Main application loop"""
    try:
        # Initialize system
        if not initialize_system():
            print("Failed to initialize system. Exiting...")
            sys.exit(1)
        
        # Display welcome message
        display_welcome()
        pause()
        
        # Main application loop
        while True:
            try:
                clear_screen()
                display_main_menu()
                
                choice = get_user_input("Enter your choice (1-7)", str, True)
                
                if not choice:
                    continue
                
                # Handle the choice
                if not handle_menu_choice(choice):
                    break
                    
            except KeyboardInterrupt:
                print("\n\nApplication interrupted by user.")
                if confirm_action("Do you want to exit the Hospital Management System?"):
                    break
                else:
                    continue
            except Exception as e:
                error_msg = f"Unexpected error in main loop: {str(e)}"
                log_error(error_msg)
                print(f"Error: {error_msg}")
                
                if not confirm_action("An error occurred. Do you want to continue?"):
                    break
                    
    except Exception as e:
        error_msg = f"Critical error in main application: {str(e)}"
        log_error(error_msg)
        print(f"Critical Error: {error_msg}")
        print("The application will now exit.")
        sys.exit(1)

def run_quick_demo():
    """Run a quick demonstration of the system"""
    try:
        print("\n" + "=" * 60)
        print("           QUICK SYSTEM DEMONSTRATION")
        print("=" * 60)
        
        # Add sample data
        print("\n1. Adding sample patient...")
        sample_patient = {
            'name': 'John Doe',
            'age': 35,
            'gender': 'Male',
            'contact': '555-0123',
            'medical_history': 'No known allergies'
        }
        patient_management.add_patient(sample_patient)
        
        print("\n2. Adding sample doctor...")
        sample_doctor = {
            'name': 'Dr. Sarah Smith',
            'role': 'Doctor',
            'contact': '555-0456',
            'specialization': 'General Medicine'
        }
        staff_management.add_staff(sample_doctor)
        
        print("\n3. Displaying system statistics...")
        display_system_info()
        
        print("\nDemo completed! You can now use the full system.")
        
    except Exception as e:
        error_msg = f"Error in demo: {str(e)}"
        log_error(error_msg)
        print(f"Demo Error: {error_msg}")

if __name__ == "__main__":
    try:
        # Check if demo mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == '--demo':
            if initialize_system():
                run_quick_demo()
        else:
            # Run the main application
            main()
            
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

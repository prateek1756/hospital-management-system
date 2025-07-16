"""
Billing Management Module for Hospital Management System
Handles billing generation, payment recording, and financial tracking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import config
import database
from models import Billing
from utils import (log_error, log_info, validate_input, print_table, 
                  get_user_input, confirm_action)
import patient_management

# Service pricing dictionary
SERVICE_PRICES = {
    'consultation': 100.0,
    'blood_test': 50.0,
    'x_ray': 150.0,
    'mri_scan': 800.0,
    'ct_scan': 600.0,
    'ultrasound': 200.0,
    'ecg': 75.0,
    'surgery_minor': 2000.0,
    'surgery_major': 10000.0,
    'emergency_visit': 300.0,
    'vaccination': 25.0,
    'physiotherapy': 80.0,
    'dental_checkup': 120.0,
    'eye_exam': 90.0,
    'prescription': 30.0
}

def display_services():
    """Display available services and their prices"""
    print("\n--- Available Services ---")
    headers = ["Service", "Price ($)"]
    rows = []
    
    for service, price in SERVICE_PRICES.items():
        service_name = service.replace('_', ' ').title()
        rows.append([service_name, f"{price:.2f}"])
    
    print_table(headers, rows)

def calculate_bill_amount(services: List[str]) -> float:
    """
    Calculate total bill amount based on services
    
    Args:
        services (List[str]): List of service codes
        
    Returns:
        float: Total amount
    """
    total = 0.0
    for service in services:
        service_key = service.lower().replace(' ', '_')
        if service_key in SERVICE_PRICES:
            total += SERVICE_PRICES[service_key]
        else:
            # If service not found, ask for custom price
            try:
                custom_price = float(get_user_input(f"Enter price for '{service}'", str, True))
                total += custom_price
            except (ValueError, TypeError):
                print(f"Invalid price for service '{service}'. Skipping.")
    
    return total

def generate_bill(patient_id: str = None, services: List[str] = None) -> bool:
    """
    Generate a new bill for a patient
    
    Args:
        patient_id (str, optional): Patient ID
        services (List[str], optional): List of services
        
    Returns:
        bool: True if bill generated successfully, False otherwise
    """
    try:
        if not patient_id or not services:
            # Interactive input
            print("\n--- Generate New Bill ---")
            
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
            
            # Display available services
            display_services()
            
            print("\nEnter services (one per line, press Enter twice to finish):")
            services = []
            while True:
                service = get_user_input("Service name (or press Enter to finish)", str, False)
                if not service:
                    break
                services.append(service)
            
            if not services:
                print("No services entered. Bill generation cancelled.")
                return False
        
        # Calculate total amount
        total_amount = calculate_bill_amount(services)
        
        if total_amount <= 0:
            print("Invalid bill amount. Bill generation cancelled.")
            return False
        
        # Create billing object
        billing = Billing(
            patient_id=patient_id,
            amount=total_amount,
            services=services,
            status='unpaid'
        )
        
        # Load existing bills
        bills_data = database.load_data(config.BILLING_FILE)
        
        # Add new bill
        bills_data.append(billing.to_dict())
        
        # Save to file
        if database.save_data(config.BILLING_FILE, bills_data):
            log_info(f"Bill generated successfully: {billing.id} for patient {patient_id}")
            print(f"Bill generated successfully!")
            print(f"Bill ID: {billing.id}")
            print(f"Total Amount: ${total_amount:.2f}")
            print(f"Services: {', '.join(services)}")
            return True
        else:
            print("Error: Failed to save bill data.")
            return False
            
    except Exception as e:
        error_msg = f"Error generating bill: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def record_payment(billing_id: str, payment_amount: float = None) -> bool:
    """
    Record a payment for a bill
    
    Args:
        billing_id (str): ID of the bill
        payment_amount (float, optional): Payment amount
        
    Returns:
        bool: True if payment recorded successfully, False otherwise
    """
    try:
        # Load existing bills
        bills_data = database.load_data(config.BILLING_FILE)
        
        # Find bill
        bill_record = database.find_by_id(bills_data, billing_id)
        if not bill_record:
            print(f"Error: Bill with ID {billing_id} not found.")
            return False
        
        if bill_record['status'] == 'paid':
            print("This bill has already been paid in full.")
            return True
        
        if not payment_amount:
            # Interactive input
            print(f"\n--- Record Payment for Bill: {billing_id[:8]}... ---")
            print(f"Total Amount: ${bill_record['amount']:.2f}")
            print(f"Current Status: {bill_record['status'].title()}")
            
            payment_amount = get_user_input("Enter payment amount", float, True)
            if payment_amount is None or payment_amount <= 0:
                print("Invalid payment amount.")
                return False
        
        # Validate payment amount
        if payment_amount > bill_record['amount']:
            print("Payment amount cannot exceed the bill total.")
            return False
        
        # Update bill status
        updated_data = {
            'payment_date': datetime.now().isoformat()
        }
        
        if payment_amount >= bill_record['amount']:
            updated_data['status'] = 'paid'
            print(f"Payment of ${payment_amount:.2f} recorded. Bill paid in full.")
        else:
            updated_data['status'] = 'partial'
            print(f"Partial payment of ${payment_amount:.2f} recorded.")
        
        # Update the record
        if database.update_record(bills_data, billing_id, updated_data):
            if database.save_data(config.BILLING_FILE, bills_data):
                log_info(f"Payment recorded successfully: ${payment_amount:.2f} for bill {billing_id}")
                print("Payment recorded successfully!")
                return True
            else:
                print("Error: Failed to save payment record.")
                return False
        else:
            print("Error: Failed to update bill record.")
            return False
            
    except Exception as e:
        error_msg = f"Error recording payment for bill {billing_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return False

def get_bill(billing_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific bill record
    
    Args:
        billing_id (str): ID of the bill to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Bill record or None if not found
    """
    try:
        bills_data = database.load_data(config.BILLING_FILE)
        bill_record = database.find_by_id(bills_data, billing_id)
        
        if bill_record:
            # Get patient name for display
            patient = patient_management.get_patient(bill_record['patient_id'])
            patient_name = patient['name'] if patient else 'Unknown'
            
            print(f"\n--- Bill Details ---")
            print(f"Bill ID: {bill_record['id']}")
            print(f"Patient: {patient_name}")
            print(f"Amount: ${bill_record['amount']:.2f}")
            print(f"Status: {bill_record['status'].title()}")
            print(f"Services: {', '.join(bill_record['services'])}")
            print(f"Created: {bill_record['created_at'][:10]}")
            if bill_record.get('payment_date'):
                print(f"Payment Date: {bill_record['payment_date'][:10]}")
            
            return bill_record
        else:
            print(f"Bill with ID {billing_id} not found.")
            return None
            
    except Exception as e:
        error_msg = f"Error retrieving bill {billing_id}: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return None

def list_bills(status_filter: str = None) -> List[Dict[str, Any]]:
    """
    List all bills with optional status filter
    
    Args:
        status_filter (str, optional): Filter by bill status
        
    Returns:
        List[Dict[str, Any]]: List of bill records
    """
    try:
        bills_data = database.load_data(config.BILLING_FILE)
        
        if not bills_data:
            print("No bills found in the system.")
            return []
        
        # Filter by status if specified
        if status_filter:
            bills_data = [bill for bill in bills_data 
                         if bill['status'].lower() == status_filter.lower()]
        
        if not bills_data:
            status_msg = f" with status '{status_filter}'" if status_filter else ""
            print(f"No bills found{status_msg}.")
            return []
        
        # Get patient names for display
        patients_data = database.load_data(config.PATIENTS_FILE)
        patient_names = {p['id']: p['name'] for p in patients_data}
        
        # Display bills in a table format
        headers = ["ID", "Patient", "Amount ($)", "Status", "Services", "Date"]
        rows = []
        
        for bill in bills_data:
            patient_name = patient_names.get(bill['patient_id'], 'Unknown')
            services = ', '.join(bill['services'])
            if len(services) > 30:
                services = services[:27] + "..."
            
            rows.append([
                bill['id'][:8] + "...",
                patient_name,
                f"{bill['amount']:.2f}",
                bill['status'].title(),
                services,
                bill['created_at'][:10]
            ])
        
        status_msg = f" ({status_filter.title()})" if status_filter else ""
        print(f"\n--- Bills List{status_msg} ({len(bills_data)} bills) ---")
        print_table(headers, rows)
        
        return bills_data
        
    except Exception as e:
        error_msg = f"Error listing bills: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def get_outstanding_bills() -> List[Dict[str, Any]]:
    """
    Get all unpaid and partially paid bills
    
    Returns:
        List[Dict[str, Any]]: List of outstanding bills
    """
    try:
        bills_data = database.load_data(config.BILLING_FILE)
        
        outstanding_bills = [bill for bill in bills_data 
                           if bill['status'] in ['unpaid', 'partial']]
        
        if outstanding_bills:
            total_outstanding = sum(bill['amount'] for bill in outstanding_bills)
            print(f"\n--- Outstanding Bills ({len(outstanding_bills)} bills) ---")
            print(f"Total Outstanding Amount: ${total_outstanding:.2f}")
            list_bills()
        else:
            print("No outstanding bills found.")
        
        return outstanding_bills
        
    except Exception as e:
        error_msg = f"Error getting outstanding bills: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def get_patient_bills(patient_id: str) -> List[Dict[str, Any]]:
    """
    Get all bills for a specific patient
    
    Args:
        patient_id (str): Patient ID
        
    Returns:
        List[Dict[str, Any]]: List of patient's bills
    """
    try:
        bills_data = database.load_data(config.BILLING_FILE)
        
        patient_bills = [bill for bill in bills_data 
                        if bill['patient_id'] == patient_id]
        
        if patient_bills:
            patient = patient_management.get_patient(patient_id)
            patient_name = patient['name'] if patient else 'Unknown'
            
            total_amount = sum(bill['amount'] for bill in patient_bills)
            paid_bills = [bill for bill in patient_bills if bill['status'] == 'paid']
            outstanding_amount = sum(bill['amount'] for bill in patient_bills 
                                   if bill['status'] in ['unpaid', 'partial'])
            
            print(f"\n--- Bills for {patient_name} ---")
            print(f"Total Bills: {len(patient_bills)}")
            print(f"Total Amount: ${total_amount:.2f}")
            print(f"Paid Bills: {len(paid_bills)}")
            print(f"Outstanding Amount: ${outstanding_amount:.2f}")
            
            # Display bills
            headers = ["ID", "Amount ($)", "Status", "Services", "Date"]
            rows = []
            
            for bill in patient_bills:
                services = ', '.join(bill['services'])
                if len(services) > 30:
                    services = services[:27] + "..."
                
                rows.append([
                    bill['id'][:8] + "...",
                    f"{bill['amount']:.2f}",
                    bill['status'].title(),
                    services,
                    bill['created_at'][:10]
                ])
            
            print_table(headers, rows)
        else:
            print(f"No bills found for patient ID: {patient_id}")
        
        return patient_bills
        
    except Exception as e:
        error_msg = f"Error getting patient bills: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return []

def billing_management_menu():
    """Display billing management menu and handle user choices"""
    while True:
        try:
            print("\n" + "=" * 50)
            print("         BILLING MANAGEMENT")
            print("=" * 50)
            print("1. Generate New Bill")
            print("2. View All Bills")
            print("3. View Outstanding Bills")
            print("4. Record Payment")
            print("5. View Bill Details")
            print("6. View Patient Bills")
            print("7. View Service Prices")
            print("8. Back to Main Menu")
            print("-" * 50)
            
            choice = get_user_input("Enter your choice (1-8)", str, True)
            
            if choice == '1':
                generate_bill()
            elif choice == '2':
                list_bills()
            elif choice == '3':
                get_outstanding_bills()
            elif choice == '4':
                billing_id = get_user_input("Enter Bill ID for payment", str, True)
                if billing_id:
                    record_payment(billing_id)
            elif choice == '5':
                billing_id = get_user_input("Enter Bill ID to view", str, True)
                if billing_id:
                    get_bill(billing_id)
            elif choice == '6':
                patient_id = get_user_input("Enter Patient ID", str, True)
                if patient_id:
                    get_patient_bills(patient_id)
            elif choice == '7':
                display_services()
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 8.")
                
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            break
        except Exception as e:
            log_error(f"Error in billing management menu: {str(e)}")
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    billing_management_menu()

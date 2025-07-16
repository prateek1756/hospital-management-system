"""
Reports Module for Hospital Management System
Generates various reports based on system data
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import config
import database
from utils import log_error, log_info, print_table, get_user_input, validate_date

def daily_report(date: str = None) -> Dict[str, Any]:
    """
    Generate daily report for hospital activities
    
    Args:
        date (str, optional): Date for report (YYYY-MM-DD), defaults to today
        
    Returns:
        Dict[str, Any]: Daily report data
    """
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        elif not validate_date(date):
            print("Invalid date format. Using today's date.")
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n{'='*60}")
        print(f"           DAILY REPORT - {date}")
        print(f"{'='*60}")
        
        # Load all data
        patients_data = database.load_data(config.PATIENTS_FILE)
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        bills_data = database.load_data(config.BILLING_FILE)
        staff_data = database.load_data(config.STAFF_FILE)
        
        # Filter data for the specific date
        daily_appointments = [apt for apt in appointments_data if apt['date'] == date]
        daily_bills = [bill for bill in bills_data if bill['created_at'][:10] == date]
        daily_patients = [patient for patient in patients_data if patient['created_at'][:10] == date]
        
        # Calculate statistics
        total_appointments = len(daily_appointments)
        completed_appointments = len([apt for apt in daily_appointments if apt['status'] == 'completed'])
        cancelled_appointments = len([apt for apt in daily_appointments if apt['status'] == 'cancelled'])
        scheduled_appointments = len([apt for apt in daily_appointments if apt['status'] == 'scheduled'])
        
        total_revenue = sum(bill['amount'] for bill in daily_bills)
        new_patients = len(daily_patients)
        
        # Display summary
        print(f"\n--- SUMMARY ---")
        print(f"New Patients Registered: {new_patients}")
        print(f"Total Appointments: {total_appointments}")
        print(f"  - Completed: {completed_appointments}")
        print(f"  - Scheduled: {scheduled_appointments}")
        print(f"  - Cancelled: {cancelled_appointments}")
        print(f"Bills Generated: {len(daily_bills)}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        
        # Appointments by doctor
        if daily_appointments:
            print(f"\n--- APPOINTMENTS BY DOCTOR ---")
            doctor_appointments = defaultdict(int)
            doctor_names = {s['id']: s['name'] for s in staff_data if s['role'].lower() == 'doctor'}
            
            for apt in daily_appointments:
                doctor_name = doctor_names.get(apt['doctor_id'], 'Unknown')
                doctor_appointments[doctor_name] += 1
            
            headers = ["Doctor", "Appointments"]
            rows = [[doctor, str(count)] for doctor, count in doctor_appointments.items()]
            print_table(headers, rows)
        
        # Revenue breakdown
        if daily_bills:
            print(f"\n--- REVENUE BREAKDOWN ---")
            service_revenue = defaultdict(float)
            
            for bill in daily_bills:
                for service in bill['services']:
                    service_revenue[service] += bill['amount'] / len(bill['services'])
            
            headers = ["Service", "Revenue ($)"]
            rows = [[service, f"{revenue:.2f}"] for service, revenue in service_revenue.items()]
            print_table(headers, rows)
        
        report_data = {
            'date': date,
            'new_patients': new_patients,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'scheduled_appointments': scheduled_appointments,
            'bills_generated': len(daily_bills),
            'total_revenue': total_revenue,
            'doctor_appointments': dict(doctor_appointments) if daily_appointments else {},
            'service_revenue': dict(service_revenue) if daily_bills else {}
        }
        
        log_info(f"Daily report generated for {date}")
        return report_data
        
    except Exception as e:
        error_msg = f"Error generating daily report: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return {}

def monthly_report(year: int = None, month: int = None) -> Dict[str, Any]:
    """
    Generate monthly report for hospital activities
    
    Args:
        year (int, optional): Year for report, defaults to current year
        month (int, optional): Month for report, defaults to current month
        
    Returns:
        Dict[str, Any]: Monthly report data
    """
    try:
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        month_name = datetime(year, month, 1).strftime('%B')
        
        print(f"\n{'='*60}")
        print(f"        MONTHLY REPORT - {month_name} {year}")
        print(f"{'='*60}")
        
        # Load all data
        patients_data = database.load_data(config.PATIENTS_FILE)
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        bills_data = database.load_data(config.BILLING_FILE)
        staff_data = database.load_data(config.STAFF_FILE)
        
        # Filter data for the specific month
        month_str = f"{year}-{month:02d}"
        monthly_appointments = [apt for apt in appointments_data if apt['date'].startswith(month_str)]
        monthly_bills = [bill for bill in bills_data if bill['created_at'].startswith(month_str)]
        monthly_patients = [patient for patient in patients_data if patient['created_at'].startswith(month_str)]
        
        # Calculate statistics
        total_appointments = len(monthly_appointments)
        completed_appointments = len([apt for apt in monthly_appointments if apt['status'] == 'completed'])
        cancelled_appointments = len([apt for apt in monthly_appointments if apt['status'] == 'cancelled'])
        
        total_revenue = sum(bill['amount'] for bill in monthly_bills)
        paid_bills = [bill for bill in monthly_bills if bill['status'] == 'paid']
        outstanding_bills = [bill for bill in monthly_bills if bill['status'] in ['unpaid', 'partial']]
        
        new_patients = len(monthly_patients)
        
        # Display summary
        print(f"\n--- MONTHLY SUMMARY ---")
        print(f"New Patients: {new_patients}")
        print(f"Total Appointments: {total_appointments}")
        print(f"  - Completed: {completed_appointments}")
        print(f"  - Cancelled: {cancelled_appointments}")
        print(f"Bills Generated: {len(monthly_bills)}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        print(f"Paid Bills: {len(paid_bills)}")
        print(f"Outstanding Bills: {len(outstanding_bills)}")
        
        # Daily breakdown
        if monthly_appointments or monthly_bills:
            print(f"\n--- DAILY BREAKDOWN ---")
            daily_stats = defaultdict(lambda: {'appointments': 0, 'revenue': 0.0})
            
            for apt in monthly_appointments:
                day = apt['date']
                daily_stats[day]['appointments'] += 1
            
            for bill in monthly_bills:
                day = bill['created_at'][:10]
                daily_stats[day]['revenue'] += bill['amount']
            
            headers = ["Date", "Appointments", "Revenue ($)"]
            rows = []
            for date in sorted(daily_stats.keys()):
                stats = daily_stats[date]
                rows.append([date, str(stats['appointments']), f"{stats['revenue']:.2f}"])
            
            if rows:
                print_table(headers, rows)
        
        # Top performing doctors
        if monthly_appointments:
            print(f"\n--- TOP PERFORMING DOCTORS ---")
            doctor_stats = defaultdict(lambda: {'appointments': 0, 'completed': 0})
            doctor_names = {s['id']: s['name'] for s in staff_data if s['role'].lower() == 'doctor'}
            
            for apt in monthly_appointments:
                doctor_name = doctor_names.get(apt['doctor_id'], 'Unknown')
                doctor_stats[doctor_name]['appointments'] += 1
                if apt['status'] == 'completed':
                    doctor_stats[doctor_name]['completed'] += 1
            
            headers = ["Doctor", "Total Appointments", "Completed", "Completion Rate (%)"]
            rows = []
            for doctor, stats in doctor_stats.items():
                completion_rate = (stats['completed'] / stats['appointments'] * 100) if stats['appointments'] > 0 else 0
                rows.append([
                    doctor,
                    str(stats['appointments']),
                    str(stats['completed']),
                    f"{completion_rate:.1f}"
                ])
            
            # Sort by total appointments
            rows.sort(key=lambda x: int(x[1]), reverse=True)
            print_table(headers, rows)
        
        report_data = {
            'year': year,
            'month': month,
            'month_name': month_name,
            'new_patients': new_patients,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'bills_generated': len(monthly_bills),
            'total_revenue': total_revenue,
            'paid_bills': len(paid_bills),
            'outstanding_bills': len(outstanding_bills)
        }
        
        log_info(f"Monthly report generated for {month_name} {year}")
        return report_data
        
    except Exception as e:
        error_msg = f"Error generating monthly report: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return {}

def patient_summary_report() -> Dict[str, Any]:
    """
    Generate patient summary report
    
    Returns:
        Dict[str, Any]: Patient summary data
    """
    try:
        print(f"\n{'='*60}")
        print(f"           PATIENT SUMMARY REPORT")
        print(f"{'='*60}")
        
        # Load data
        patients_data = database.load_data(config.PATIENTS_FILE)
        appointments_data = database.load_data(config.APPOINTMENTS_FILE)
        bills_data = database.load_data(config.BILLING_FILE)
        
        if not patients_data:
            print("No patients found in the system.")
            return {}
        
        total_patients = len(patients_data)
        
        # Gender distribution
        gender_count = defaultdict(int)
        age_groups = defaultdict(int)
        
        for patient in patients_data:
            gender_count[patient['gender']] += 1
            
            age = patient['age']
            if age < 18:
                age_groups['0-17'] += 1
            elif age < 30:
                age_groups['18-29'] += 1
            elif age < 50:
                age_groups['30-49'] += 1
            elif age < 65:
                age_groups['50-64'] += 1
            else:
                age_groups['65+'] += 1
        
        print(f"\n--- PATIENT DEMOGRAPHICS ---")
        print(f"Total Patients: {total_patients}")
        
        print(f"\nGender Distribution:")
        for gender, count in gender_count.items():
            percentage = (count / total_patients) * 100
            print(f"  {gender}: {count} ({percentage:.1f}%)")
        
        print(f"\nAge Distribution:")
        for age_group, count in age_groups.items():
            percentage = (count / total_patients) * 100
            print(f"  {age_group}: {count} ({percentage:.1f}%)")
        
        # Patient activity
        patient_appointments = defaultdict(int)
        patient_bills = defaultdict(float)
        
        for apt in appointments_data:
            patient_appointments[apt['patient_id']] += 1
        
        for bill in bills_data:
            patient_bills[bill['patient_id']] += bill['amount']
        
        # Most active patients
        if patient_appointments:
            print(f"\n--- MOST ACTIVE PATIENTS (by appointments) ---")
            patient_names = {p['id']: p['name'] for p in patients_data}
            
            # Sort patients by appointment count
            sorted_patients = sorted(patient_appointments.items(), key=lambda x: x[1], reverse=True)[:10]
            
            headers = ["Patient", "Appointments", "Total Billing ($)"]
            rows = []
            for patient_id, apt_count in sorted_patients:
                patient_name = patient_names.get(patient_id, 'Unknown')
                total_billing = patient_bills.get(patient_id, 0.0)
                rows.append([patient_name, str(apt_count), f"{total_billing:.2f}"])
            
            print_table(headers, rows)
        
        report_data = {
            'total_patients': total_patients,
            'gender_distribution': dict(gender_count),
            'age_distribution': dict(age_groups),
            'most_active_patients': dict(sorted_patients[:5]) if patient_appointments else {}
        }
        
        log_info("Patient summary report generated")
        return report_data
        
    except Exception as e:
        error_msg = f"Error generating patient summary report: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return {}

def financial_report(start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """
    Generate financial report for a date range
    
    Args:
        start_date (str, optional): Start date (YYYY-MM-DD)
        end_date (str, optional): End date (YYYY-MM-DD)
        
    Returns:
        Dict[str, Any]: Financial report data
    """
    try:
        if not start_date:
            # Default to current month
            start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n{'='*60}")
        print(f"    FINANCIAL REPORT ({start_date} to {end_date})")
        print(f"{'='*60}")
        
        # Load bills data
        bills_data = database.load_data(config.BILLING_FILE)
        
        # Filter bills by date range
        filtered_bills = []
        for bill in bills_data:
            bill_date = bill['created_at'][:10]
            if start_date <= bill_date <= end_date:
                filtered_bills.append(bill)
        
        if not filtered_bills:
            print("No bills found for the specified date range.")
            return {}
        
        # Calculate financial metrics
        total_revenue = sum(bill['amount'] for bill in filtered_bills)
        paid_bills = [bill for bill in filtered_bills if bill['status'] == 'paid']
        unpaid_bills = [bill for bill in filtered_bills if bill['status'] == 'unpaid']
        partial_bills = [bill for bill in filtered_bills if bill['status'] == 'partial']
        
        collected_revenue = sum(bill['amount'] for bill in paid_bills)
        outstanding_revenue = sum(bill['amount'] for bill in unpaid_bills + partial_bills)
        
        print(f"\n--- FINANCIAL SUMMARY ---")
        print(f"Total Bills: {len(filtered_bills)}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        print(f"Collected Revenue: ${collected_revenue:.2f}")
        print(f"Outstanding Revenue: ${outstanding_revenue:.2f}")
        print(f"Collection Rate: {(collected_revenue/total_revenue*100):.1f}%" if total_revenue > 0 else "Collection Rate: 0%")
        
        # Revenue by service
        service_revenue = defaultdict(float)
        service_count = defaultdict(int)
        
        for bill in filtered_bills:
            for service in bill['services']:
                service_revenue[service] += bill['amount'] / len(bill['services'])
                service_count[service] += 1
        
        if service_revenue:
            print(f"\n--- REVENUE BY SERVICE ---")
            headers = ["Service", "Count", "Revenue ($)", "Avg per Service ($)"]
            rows = []
            
            for service in sorted(service_revenue.keys(), key=lambda x: service_revenue[x], reverse=True):
                revenue = service_revenue[service]
                count = service_count[service]
                avg_revenue = revenue / count if count > 0 else 0
                
                rows.append([
                    service.replace('_', ' ').title(),
                    str(count),
                    f"{revenue:.2f}",
                    f"{avg_revenue:.2f}"
                ])
            
            print_table(headers, rows)
        
        # Payment status breakdown
        print(f"\n--- PAYMENT STATUS ---")
        headers = ["Status", "Count", "Amount ($)", "Percentage"]
        rows = [
            ["Paid", str(len(paid_bills)), f"{sum(bill['amount'] for bill in paid_bills):.2f}", 
             f"{len(paid_bills)/len(filtered_bills)*100:.1f}%"],
            ["Unpaid", str(len(unpaid_bills)), f"{sum(bill['amount'] for bill in unpaid_bills):.2f}", 
             f"{len(unpaid_bills)/len(filtered_bills)*100:.1f}%"],
            ["Partial", str(len(partial_bills)), f"{sum(bill['amount'] for bill in partial_bills):.2f}", 
             f"{len(partial_bills)/len(filtered_bills)*100:.1f}%"]
        ]
        print_table(headers, rows)
        
        report_data = {
            'start_date': start_date,
            'end_date': end_date,
            'total_bills': len(filtered_bills),
            'total_revenue': total_revenue,
            'collected_revenue': collected_revenue,
            'outstanding_revenue': outstanding_revenue,
            'collection_rate': (collected_revenue/total_revenue*100) if total_revenue > 0 else 0,
            'service_revenue': dict(service_revenue)
        }
        
        log_info(f"Financial report generated for {start_date} to {end_date}")
        return report_data
        
    except Exception as e:
        error_msg = f"Error generating financial report: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return {}

def custom_report(criteria: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate custom report based on user-defined criteria
    
    Args:
        criteria (Dict[str, Any]): Report criteria
        
    Returns:
        Dict[str, Any]: Custom report data
    """
    try:
        print(f"\n{'='*60}")
        print(f"              CUSTOM REPORT")
        print(f"{'='*60}")
        
        # This is a flexible function that can be extended based on requirements
        # For now, it provides basic filtering capabilities
        
        report_type = criteria.get('type', 'summary')
        date_range = criteria.get('date_range', {})
        filters = criteria.get('filters', {})
        
        if report_type == 'appointments':
            appointments_data = database.load_data(config.APPOINTMENTS_FILE)
            filtered_data = appointments_data
            
            # Apply filters
            if 'status' in filters:
                filtered_data = [apt for apt in filtered_data if apt['status'] == filters['status']]
            
            if 'date_from' in date_range and 'date_to' in date_range:
                filtered_data = [apt for apt in filtered_data 
                               if date_range['date_from'] <= apt['date'] <= date_range['date_to']]
            
            print(f"Filtered Appointments: {len(filtered_data)}")
            
            if filtered_data:
                # Display appointments
                headers = ["ID", "Patient ID", "Doctor ID", "Date", "Time", "Status"]
                rows = []
                for apt in filtered_data[:20]:  # Limit to first 20 results
                    rows.append([
                        apt['id'][:8] + "...",
                        apt['patient_id'][:8] + "...",
                        apt['doctor_id'][:8] + "...",
                        apt['date'],
                        apt['time'],
                        apt['status'].title()
                    ])
                
                print_table(headers, rows)
                if len(filtered_data) > 20:
                    print(f"... and {len(filtered_data) - 20} more appointments")
        
        elif report_type == 'summary':
            # Generate overall system summary
            patients_data = database.load_data(config.PATIENTS_FILE)
            appointments_data = database.load_data(config.APPOINTMENTS_FILE)
            bills_data = database.load_data(config.BILLING_FILE)
            staff_data = database.load_data(config.STAFF_FILE)
            
            print(f"--- SYSTEM SUMMARY ---")
            print(f"Total Patients: {len(patients_data)}")
            print(f"Total Staff: {len(staff_data)}")
            print(f"Total Appointments: {len(appointments_data)}")
            print(f"Total Bills: {len(bills_data)}")
            
            if bills_data:
                total_revenue = sum(bill['amount'] for bill in bills_data)
                print(f"Total Revenue: ${total_revenue:.2f}")
        
        log_info(f"Custom report generated with criteria: {criteria}")
        return {'criteria': criteria, 'generated': True}
        
    except Exception as e:
        error_msg = f"Error generating custom report: {str(e)}"
        log_error(error_msg)
        print(f"Error: {error_msg}")
        return {}

def reports_menu():
    """Display reports menu and handle user choices"""
    while True:
        try:
            print("\n" + "=" * 50)
            print("              REPORTS")
            print("=" * 50)
            print("1. Daily Report")
            print("2. Monthly Report")
            print("3. Patient Summary Report")
            print("4. Financial Report")
            print("5. Custom Report")
            print("6. Back to Main Menu")
            print("-" * 50)
            
            choice = get_user_input("Enter your choice (1-6)", str, True)
            
            if choice == '1':
                date = get_user_input("Enter date (YYYY-MM-DD) or press Enter for today", str, False)
                daily_report(date)
            elif choice == '2':
                year = get_user_input("Enter year or press Enter for current year", str, False)
                month = get_user_input("Enter month (1-12) or press Enter for current month", str, False)
                
                try:
                    year = int(year) if year else None
                    month = int(month) if month else None
                except ValueError:
                    year = month = None
                
                monthly_report(year, month)
            elif choice == '3':
                patient_summary_report()
            elif choice == '4':
                start_date = get_user_input("Enter start date (YYYY-MM-DD) or press Enter for current month", str, False)
                end_date = get_user_input("Enter end date (YYYY-MM-DD) or press Enter for today", str, False)
                financial_report(start_date, end_date)
            elif choice == '5':
                print("Custom Report Options:")
                print("1. Appointments Summary")
                print("2. System Summary")
                
                report_choice = get_user_input("Enter report type (1-2)", str, True)
                
                if report_choice == '1':
                    criteria = {'type': 'appointments'}
                    status_filter = get_user_input("Filter by status (scheduled/completed/cancelled) or press Enter for all", str, False)
                    if status_filter:
                        criteria['filters'] = {'status': status_filter}
                    custom_report(criteria)
                elif report_choice == '2':
                    custom_report({'type': 'summary'})
                else:
                    print("Invalid choice.")
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
                
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            break
        except Exception as e:
            log_error(f"Error in reports menu: {str(e)}")
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    reports_menu()
